"""
DataHerd Server Utilities

This module contains utility functions for the DataHerd server.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from config.config import SQLALCHEMY_DATABASE_URI
import logging

engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency to get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_and_initialize_db():
    """
    Check and initialize database if needed.
    """
    try:
        # Test database connection
        with engine.connect() as connection:
            logging.info("Database connection successful")
            return True
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return False

