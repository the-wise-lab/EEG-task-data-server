import os
import csv
from datetime import datetime
from flask import jsonify
from .. import config


def format_timestamp(epoch_ms):
    """Convert epoch milliseconds to a readable timestamp string and separate date/time."""
    try:
        epoch_seconds = epoch_ms / 1000.0
        dt = datetime.fromtimestamp(epoch_seconds)
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M:%S.%f")[:-3]  # Trim to milliseconds
        return date_str, time_str
    except (ValueError, TypeError):
        return str(epoch_ms), ""


def submit_data_handler(request, logger):
    """Handle the submit_data endpoint request."""
    try:
        data = request.get_json()

        if not data:
            logger.warning("No data provided in request")
            return jsonify({"error": "No data provided"}), 400

        if "id" not in data or "session" not in data or "data" not in data:
            logger.warning("Missing required fields in request")
            return (
                jsonify(
                    {"error": "Missing required fields: id, session, or data"}
                ),
                400,
            )

        if not isinstance(data["data"], list):
            logger.warning("Data field must be a list")
            return jsonify({"error": "Data field must be a list"}), 400

        participant_id = str(data["id"])
        session_id = str(data["session"])
        data_points = data["data"]
        task_name = str(data.get("task", "unknown"))
        write_mode = data.get("write_mode", config.DEFAULT_WRITE_MODE).lower()

        if write_mode not in ["append", "overwrite"]:
            write_mode = config.DEFAULT_WRITE_MODE
            logger.warning(
                f"Invalid write_mode specified, using default: {write_mode}"
            )

        logger.info(
            f"Received data for participant {participant_id}, session {session_id}, task {task_name} with write_mode={write_mode}"
        )

        task_dir = os.path.join(config.DATA_DIR, task_name)
        os.makedirs(task_dir, exist_ok=True)

        filename = os.path.join(
            task_dir, f"participant_{participant_id}_session_{session_id}.csv"
        )

        logger.info(f"Using task-specific directory: {task_dir}")

        if not data_points:
            logger.warning("No data points provided in the data list")
            return (
                jsonify({"error": "No data points provided in the data list"}),
                400,
            )

        processed_data_points = []
        for point in data_points:
            processed_point = point.copy()
            processed_point["participant_id"] = participant_id
            processed_point["session_id"] = session_id
            processed_point["task"] = task_name

            if "time" in processed_point and isinstance(
                processed_point["time"], (int, float)
            ):
                original_time = processed_point["time"]
                date_str, time_str = format_timestamp(original_time)
                processed_point["date"] = date_str
                processed_point["time"] = time_str
                if "timestamp" in processed_point:
                    del processed_point["timestamp"]

            processed_data_points.append(processed_point)

        all_keys = set()
        for point in processed_data_points:
            all_keys.update(point.keys())

        existing_data = []
        file_exists = os.path.isfile(filename)

        if file_exists and write_mode == "append":
            logger.info(f"Appending to existing file: {filename}")
            with open(filename, "r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                if reader.fieldnames:
                    all_keys.update(reader.fieldnames)
                for row in reader:
                    if (
                        "timestamp" in row
                        and "date" not in row
                        and "time" not in row
                    ):
                        try:
                            dt = datetime.strptime(
                                row["timestamp"], "%Y-%m-%d %H:%M:%S.%f"
                            )
                            row["date"] = dt.strftime("%Y-%m-%d")
                            row["time"] = dt.strftime("%H:%M:%S.%f")[:-3]
                            del row["timestamp"]
                        except (ValueError, TypeError):
                            pass
                    existing_data.append(row)
        elif file_exists and write_mode == "overwrite":
            logger.info(f"Overwriting existing file: {filename}")
        else:
            logger.info(f"Creating new file: {filename}")

        all_keys.discard("timestamp")
        priority_headers = [
            "participant_id",
            "session_id",
            "task",
            "date",
            "time",
            "value",
            "marker",
        ]
        remaining_headers = sorted(list(all_keys - set(priority_headers)))
        headers = [
            h for h in priority_headers if h in all_keys
        ] + remaining_headers

        combined_data = (
            existing_data + processed_data_points
            if write_mode == "append"
            else processed_data_points
        )

        with open(filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(combined_data)

        action = (
            "appended to"
            if file_exists and write_mode == "append"
            else "overwritten" if file_exists else "created"
        )
        logger.info(
            f"Successfully {action} data for participant {participant_id}, session {session_id}, task {task_name}"
        )

        rel_filename = os.path.relpath(filename, start=config.DATA_DIR)
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Data {action} for participant {participant_id}, session {session_id}, task {task_name}",
                    "filename": filename,
                    "task_dir": task_dir,
                    "records_added": len(data_points),
                    "total_records": len(combined_data),
                    "write_mode": write_mode,
                }
            ),
            200,
        )

    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": str(e)}), 500
