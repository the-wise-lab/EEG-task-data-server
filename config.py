import os
import yaml

# Default configuration
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 5000
THREADS = 4

# Application configuration
DATA_DIR = 'data'  # Default directory is 'data'
LOGS_DIR = 'logs'  # Default directory is 'logs'
DEFAULT_WRITE_MODE = 'append'  # Default write mode is append

# Error reporting configuration
SENTRY_DSN = ""  # Empty string means Sentry is disabled
SENTRY_ENVIRONMENT = "development"
SENTRY_TRACES_SAMPLE_RATE = 0.2

# Load configuration from YAML file if it exists
yaml_config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
if os.path.exists(yaml_config_path):
    try:
        with open(yaml_config_path, 'r') as yaml_file:
            yaml_config = yaml.safe_load(yaml_file)
            if yaml_config:
                # Update configuration with YAML values
                if 'host' in yaml_config:
                    HOST = yaml_config['host']
                if 'port' in yaml_config:
                    PORT = yaml_config['port']
                if 'threads' in yaml_config:
                    THREADS = yaml_config['threads']
                if 'data_dir' in yaml_config:
                    DATA_DIR = yaml_config['data_dir']
                if 'logs_dir' in yaml_config:
                    LOGS_DIR = yaml_config['logs_dir']
                if 'default_write_mode' in yaml_config:
                    DEFAULT_WRITE_MODE = yaml_config['default_write_mode']
                # Error reporting config
                if 'sentry_dsn' in yaml_config:
                    SENTRY_DSN = yaml_config['sentry_dsn']
                if 'sentry_environment' in yaml_config:
                    SENTRY_ENVIRONMENT = yaml_config['sentry_environment']
                if 'sentry_traces_sample_rate' in yaml_config:
                    SENTRY_TRACES_SAMPLE_RATE = yaml_config['sentry_traces_sample_rate']
    except Exception as e:
        print(f"Error loading YAML configuration: {e}")

# Override with environment variables if they exist
if os.environ.get('EEG_DATA_DIR'):
    DATA_DIR = os.environ.get('EEG_DATA_DIR')
if os.environ.get('EEG_LOGS_DIR'):
    LOGS_DIR = os.environ.get('EEG_LOGS_DIR')
if os.environ.get('EEG_DEFAULT_WRITE_MODE'):
    DEFAULT_WRITE_MODE = os.environ.get('EEG_DEFAULT_WRITE_MODE')
if os.environ.get('EEG_SENTRY_DSN'):
    SENTRY_DSN = os.environ.get('EEG_SENTRY_DSN')
if os.environ.get('EEG_SENTRY_ENVIRONMENT'):
    SENTRY_ENVIRONMENT = os.environ.get('EEG_SENTRY_ENVIRONMENT')

# Ensure directories exist
def ensure_directories():
    """Create data and logs directories if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    return DATA_DIR, LOGS_DIR
