"""Configuration handling for the local data storage server."""
import os
import yaml

# Default configuration
HOST = '0.0.0.0'
PORT = 5000
THREADS = 4
DEFAULT_WRITE_MODE = 'append'
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')

# Sentry configuration
SENTRY_DSN = None
SENTRY_ENVIRONMENT = 'development'
SENTRY_TRACES_SAMPLE_RATE = 1.0

def load_config(config_path=None):
    """Load configuration from YAML file if it exists."""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yml')
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            if config:
                globals().update(config)

def ensure_directories():
    """Ensure data and logs directories exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    return DATA_DIR, LOGS_DIR

# Load configuration at module import
load_config()