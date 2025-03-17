from waitress import serve
from app import app
import logging
import config
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Configure logging for waitress
config.ensure_directories()  # Make sure directories exist

logging.basicConfig(
    filename=f"{config.LOGS_DIR}/server.log",
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Initialize Sentry SDK if DSN is provided
if config.SENTRY_DSN:
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        environment=config.SENTRY_ENVIRONMENT,
        traces_sample_rate=config.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            FlaskIntegration(),
        ],
    )
    logging.info("Sentry error reporting initialized")
else:
    logging.info("Sentry error reporting disabled (no DSN provided)")

if __name__ == "__main__":
    host = config.HOST
    port = config.PORT
    threads = config.THREADS

    print(
        f"Starting server on {host}:{port} at {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', 0, None, None))}"
    )
    logging.info(f"Starting server on {host}:{port}")
    logging.info(f"Using data directory: {config.DATA_DIR}")
    logging.info(f"Using logs directory: {config.LOGS_DIR}")

    serve(app, host=host, port=port, threads=threads)
