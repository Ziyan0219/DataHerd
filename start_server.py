#!/usr/bin/env python3
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the server
from api_server.api_router import run_api, create_app
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9000)
    
    args = parser.parse_args()
    
    app = create_app()
    run_api(host=args.host, port=args.port)