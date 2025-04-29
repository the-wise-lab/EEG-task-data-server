"""
Local Data Storage Server

A Flask application that receives JSON data via POST requests and stores it in CSV files.
"""

import argparse
from .api import create_app
from . import config

__version__ = "0.1.0"

def main():
    """Entry point for the application."""
    parser = argparse.ArgumentParser(description='Local Data Storage Server')
    parser.add_argument('--data-dir', help='Directory for storing data files')
    parser.add_argument('--logs-dir', help='Directory for storing log files')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on (default: 5000)')
    
    args = parser.parse_args()
    
    # Update config with command line arguments if provided
    if args.data_dir:
        config.DATA_DIR = args.data_dir
    if args.logs_dir:
        config.LOGS_DIR = args.logs_dir
    
    from waitress import serve
    app = create_app()
    
    print("Starting local data storage server...")
    print(f"Server address: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}")
    print(f"Data directory: {config.DATA_DIR}")
    print(f"Logs directory: {config.LOGS_DIR}")
    
    serve(app, host=args.host, port=args.port, threads=config.THREADS)