import os
import csv
import json
from flask import Flask, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
import config
import sentry_sdk

app = Flask(__name__)

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

        # Log received data
        app.logger.info(
            f"Received data for participant {participant_id}, session {session_id}"
        )

        # Create filename based on id and session
        filename = (
            f"{data_dir}/participant_{participant_id}_session_{session_id}.csv"
        )

        # Check if we have any data points
        if not data_points:
            app.logger.warning("No data points provided in the data list")
            return (
                jsonify({"error": "No data points provided in the data list"}),
                400,
            )

        # Get all unique keys from all data points for new data
        all_keys = set()
        for point in data_points:
            all_keys.update(point.keys())

        # Check if file already exists
        existing_data = []
        file_exists = os.path.isfile(filename)

        if file_exists:
            app.logger.info(f"Appending to existing file: {filename}")
            # Read existing data and headers
            with open(filename, "r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                # Update headers with any columns in the existing file
                if reader.fieldnames:
                    all_keys.update(reader.fieldnames)
                # Store existing data
                for row in reader:
                    existing_data.append(row)

        # Convert headers set to sorted list
        headers = sorted(list(all_keys))

        # Write combined data to CSV file (overwrites with all data)
        combined_data = existing_data + data_points

        with open(filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(combined_data)

        action = "appended to" if file_exists else "created"
        app.logger.info(f"Successfully {action} data for participant {participant_id}, session {session_id}")
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Data {action} for participant {participant_id}, session {session_id}",
                    "filename": filename,
                    "records_added": len(data_points),
                    "total_records": len(combined_data),
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
