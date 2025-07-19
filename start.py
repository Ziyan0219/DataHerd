#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataHerd Startup Script

This script provides a unified way to start the DataHerd application.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db.init_db import initialize_database
from api_server.api_router import create_app
import uvicorn


def setup_logging(log_level="INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        'OPENAI_API_KEY',
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file or set these variables.")
        return False
    
    print("✅ Environment variables check passed")
    return True


def init_database():
    """Initialize the database."""
    print("🔧 Initializing database...")
    try:
        initialize_database()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def build_frontend():
    """Build the frontend if needed."""
    frontend_dir = project_root / "dataherd-frontend"
    dist_dir = frontend_dir / "dist"
    
    if not frontend_dir.exists():
        print("⚠️  Frontend directory not found, skipping frontend build")
        return True
    
    if dist_dir.exists():
        print("✅ Frontend already built")
        return True
    
    print("🔧 Building frontend...")
    try:
        import subprocess
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Frontend built successfully")
            return True
        else:
            print(f"❌ Frontend build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Frontend build error: {e}")
        return False


def start_server(host="0.0.0.0", port=9000, reload=False):
    """Start the DataHerd server."""
    print(f"🚀 Starting DataHerd server on {host}:{port}")
    
    app = create_app()
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="DataHerd - Cattle Data Cleaning Agent")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=9000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--skip-db-init", action="store_true", help="Skip database initialization")
    parser.add_argument("--skip-frontend", action="store_true", help="Skip frontend build")
    parser.add_argument("--log-level", type=str, default="INFO", help="Log level")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    print("🐄 DataHerd - Intelligent Cattle Data Cleaning Agent")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Initialize database
    if not args.skip_db_init:
        if not init_database():
            sys.exit(1)
    
    # Build frontend
    if not args.skip_frontend:
        if not build_frontend():
            print("⚠️  Frontend build failed, but continuing with backend only")
    
    # Start server
    try:
        start_server(args.host, args.port, args.reload)
    except KeyboardInterrupt:
        print("\n👋 DataHerd server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

