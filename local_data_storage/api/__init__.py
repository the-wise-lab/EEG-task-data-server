from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from .. import config
from .handlers import submit_data_handler

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
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

    # Initialize Sentry if configured
    if config.SENTRY_DSN:
        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            environment=config.SENTRY_ENVIRONMENT,
            traces_sample_rate=config.SENTRY_TRACES_SAMPLE_RATE,
            integrations=[FlaskIntegration()],
        )
        app.logger.info("Sentry error reporting initialized")
    else:
        app.logger.info("Sentry error reporting disabled (no DSN provided)")

    @app.route("/submit_data", methods=["POST"])
    def submit_data():
        return submit_data_handler(request, app.logger)

    return app