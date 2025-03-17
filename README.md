# EEG Task Data Server

A Flask application that receives JSON data via POST requests and stores it in CSV files.

## Installation

### Using Python Virtual Environment

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

### Using Conda Environment

1. Clone the repository
2. Create and activate the conda environment using the environment file:

   ```bash
   conda env create -f environment.yml && conda activate eeg_task_data_server
   ```

3. Ready to use! Run the server with:

   ```bash
   python server.py
   ```

## Configuration

The application can be configured using any of the following methods (in order of precedence):

1. Environment variables
2. YAML configuration file (`config.yml`)
3. Python configuration file (`config.py`)

### Configuration Options

- **DATA_DIR**: Directory to store CSV files (default: `data/`)
  - YAML key: `data_dir`
  - Environment variable: `EEG_DATA_DIR`
- **LOGS_DIR**: Directory to store log files (default: `logs/`)
  - YAML key: `logs_dir`
  - Environment variable: `EEG_LOGS_DIR`
- **DEFAULT_WRITE_MODE**: Default behavior when writing to existing files (default: `append`)
  - YAML key: `default_write_mode`
  - Environment variable: `EEG_DEFAULT_WRITE_MODE`
  - Options: `append` or `overwrite`
- **HOST**: IP address to bind the server (default: `0.0.0.0`)
  - YAML key: `host`
- **PORT**: Port to run the server on (default: `5000`)
  - YAML key: `port`
- **THREADS**: Number of worker threads for Waitress (default: `4`)
  - YAML key: `threads`
- **SENTRY_DSN**: Glitchtip/Sentry DSN for error reporting (default: `""` - disabled)
  - YAML key: `sentry_dsn`
  - Environment variable: `EEG_SENTRY_DSN`
- **SENTRY_ENVIRONMENT**: Environment name for error reporting (default: `development`)
  - YAML key: `sentry_environment`
  - Environment variable: `EEG_SENTRY_ENVIRONMENT`
- **SENTRY_TRACES_SAMPLE_RATE**: Performance sampling rate (default: `0.2`)
  - YAML key: `sentry_traces_sample_rate`

### Example YAML Configuration

Create a `config.yml` file in the application root directory:

```yaml
# EEG Task Data Server Configuration
data_dir: /path/to/data/
logs_dir: /path/to/logs/
host: 127.0.0.1
port: 8080
threads: 8
sentry_dsn: "https://your-glitchtip-key@glitchtip.example.com/2"
sentry_environment: "production"
sentry_traces_sample_rate: 0.1
```

## Running the Server

To run the server with waitress:

```bash
python server.py
```

The server will start according to the configuration settings.

## API Usage

### Submit Data

**Endpoint:** `POST /submit_data`

**Request Format:**

```json
{
  "id": "123",
  "session": "1",
  "task": "flanker",  // Optional: identifies the task type
  "write_mode": "append",  // Optional: "append" (default) or "overwrite"
  "data": [
    {"time": 1000, "value": 0.5, "marker": "stimulus_1"},
    {"time": 2000, "value": 0.7, "marker": "response_1"}
  ]
}
```

**Response:**

```json
{
  "success": true,
  "message": "Data appended to for participant 123, session 1, task flanker",
  "filename": "data/participant_123_session_1_task_flanker.csv",
  "records_added": 2,
  "total_records": 5,
  "write_mode": "append"
}
```

## Data Storage

- CSV files will be organized by task and stored in the configured data directory with the following structure:
  ```
  data_dir/
  └── task_name/
      └── participant_{id}_session_{session}.csv
  ```
- Each row in the CSV file will contain participant ID, session ID, and task name.
- You can control how data is saved to existing files using the `write_mode` parameter:
  - `append`: Adds new data to the existing file (default)
  - `overwrite`: Replaces the existing file with only the new data
- Headers will be automatically merged if new data points have different fields.

## Error Reporting

The application uses Glitchtip (Sentry-compatible) for error reporting. To enable it:

1. Set up a Glitchtip account and create a project
2. Copy the DSN from your Glitchtip project settings
3. Add the DSN to your config.yml file or set it as an environment variable
4. Errors will be automatically reported to your Glitchtip dashboard
