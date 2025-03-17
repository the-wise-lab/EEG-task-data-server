import os
import csv
import json
from flask import Flask, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
import config
import sentry_sdk
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Configure logging
data_dir, logs_dir = config.ensure_directories()

handler = RotatingFileHandler(
    f"{logs_dir}/app.log", maxBytes=10000, backupCount=3
)
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s.%(msecs)03d %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

app.logger.info(f"Using data directory: {data_dir}")
app.logger.info(f"Using logs directory: {logs_dir}")


def format_timestamp(epoch_ms):
    """Convert epoch milliseconds to a readable timestamp string and separate date/time."""
    try:
        # Convert milliseconds to seconds
        epoch_seconds = epoch_ms / 1000.0
        # Convert to datetime
        dt = datetime.fromtimestamp(epoch_seconds)
        # Format date and time separately
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M:%S.%f")[:-3]  # Trim to milliseconds
        return date_str, time_str
    except (ValueError, TypeError):
        # Return placeholders if conversion fails
        return str(epoch_ms), ""


@app.route("/submit_data", methods=["POST"])
def submit_data():
    try:
        # Get JSON data from request
        data = request.get_json()

        # Validate JSON structure
        if not data:
            app.logger.warning("No data provided in request")
            return jsonify({"error": "No data provided"}), 400

        # Check required fields
        if "id" not in data or "session" not in data or "data" not in data:
            app.logger.warning("Missing required fields in request")
            return (
                jsonify(
                    {"error": "Missing required fields: id, session, or data"}
                ),
                400,
            )

        # Validate that data is a list of dictionaries
        if not isinstance(data["data"], list):
            app.logger.warning("Data field must be a list")
            return jsonify({"error": "Data field must be a list"}), 400

        # Extract fields
        participant_id = str(data["id"])
        session_id = str(data["session"])
        data_points = data["data"]
        
        # Extract optional task field
        task_name = str(data.get("task", "unknown"))
        
        # Get write mode - default to config value if not specified
        write_mode = data.get("write_mode", config.DEFAULT_WRITE_MODE).lower()
        
        # Validate write mode
        if write_mode not in ["append", "overwrite"]:
            write_mode = config.DEFAULT_WRITE_MODE
            app.logger.warning(f"Invalid write_mode specified, using default: {write_mode}")

        # Log received data
        app.logger.info(
            f"Received data for participant {participant_id}, session {session_id}, task {task_name} with write_mode={write_mode}"
        )

        # Create task-specific directory
        task_dir = os.path.join(data_dir, task_name)
        os.makedirs(task_dir, exist_ok=True)
        
        # Create filename based on id, session, and task in the task's directory
        filename = os.path.join(task_dir, f"participant_{participant_id}_session_{session_id}.csv")
        
        # Log the directory structure
        app.logger.info(f"Using task-specific directory: {task_dir}")

        # Check if we have any data points
        if not data_points:
            app.logger.warning("No data points provided in the data list")
            return (
                jsonify({"error": "No data points provided in the data list"}),
                400,
            )

        # Process data points - add ID, session, and task info to each row and format timestamps
        processed_data_points = []
        for point in data_points:
            # Create a copy of the point to avoid modifying the original
            processed_point = point.copy()
            
            # Add participant_id, session_id, and task_name to each data point
            processed_point["participant_id"] = participant_id
            processed_point["session_id"] = session_id
            processed_point["task"] = task_name
            
            # Format timestamp if it exists and is numeric
            if "time" in processed_point and isinstance(processed_point["time"], (int, float)):
                # Store the original time value temporarily
                original_time = processed_point["time"]
                
                # Create separate date and time fields
                date_str, time_str = format_timestamp(original_time)
                processed_point["date"] = date_str
                processed_point["time"] = time_str
                
                # Remove any timestamp field that might exist
                if "timestamp" in processed_point:
                    del processed_point["timestamp"]
            
            processed_data_points.append(processed_point)

        # Get all unique keys from all processed data points
        all_keys = set()
        for point in processed_data_points:
            all_keys.update(point.keys())

        # Check if file already exists
        existing_data = []
        file_exists = os.path.isfile(filename)

        # When reading existing data, also handle any timestamp field
        if file_exists and write_mode == "append":
            app.logger.info(f"Appending to existing file: {filename}")
            # Read existing data and headers
            with open(filename, "r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                # Update headers with any columns in the existing file
                if reader.fieldnames:
                    all_keys.update(reader.fieldnames)
                # Store existing data with possible transformation
                for row in reader:
                    # Convert any timestamp field to date/time if it exists
                    if "timestamp" in row and "date" not in row and "time" not in row:
                        try:
                            # Try to parse the timestamp
                            dt = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                            row["date"] = dt.strftime("%Y-%m-%d")
                            row["time"] = dt.strftime("%H:%M:%S.%f")[:-3]
                            del row["timestamp"]
                        except (ValueError, TypeError):
                            # If we can't parse, keep it as is
                            pass
                    existing_data.append(row)
        elif file_exists and write_mode == "overwrite":
            app.logger.info(f"Overwriting existing file: {filename}")
        else:
            app.logger.info(f"Creating new file: {filename}")

        # Convert headers set to sorted list with specific columns first
        priority_headers = ["participant_id", "session_id", "task", "date", "time", "value", "marker"]
        
        # Ensure timestamp is not in headers
        all_keys.discard("timestamp")
        
        remaining_headers = sorted(list(all_keys - set(priority_headers)))
        headers = [h for h in priority_headers if h in all_keys] + remaining_headers

        # Write combined data to CSV file
        combined_data = existing_data + processed_data_points if write_mode == "append" else processed_data_points

        with open(filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(combined_data)

        # Set appropriate action message based on file existence and write mode
        if file_exists:
            if write_mode == "append":
                action = "appended to"
            else:
                action = "overwritten"
        else:
            action = "created"
            
        app.logger.info(f"Successfully {action} data for participant {participant_id}, session {session_id}, task {task_name}")
        
        # Use os.path.relpath to make the path relative to the data directory for cleaner output
        rel_filename = os.path.relpath(filename, start=data_dir)
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Data {action} for participant {participant_id}, session {session_id}, task {task_name}",
                    "filename": filename,
                    "task_dir": task_dir,
                    "records_added": len(data_points),
                    "total_records": len(combined_data),
                    "write_mode": write_mode
                }
            ),
            200,
        )

    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        app.logger.error(error_msg)
        
        # Capture error with Sentry if configured
        if config.SENTRY_DSN:
            sentry_sdk.capture_exception(e)
            
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # For development only
    app.run(debug=True)
