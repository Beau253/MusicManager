# src/music_manager/api/dependencies.py

import logging
from pathlib import Path

from music_manager.core.config_manager import ConfigManager
from music_manager.core.database_manager import DatabaseManager

# This is a simplified way to manage global state for the API.
# In a larger application, you might use a more robust dependency injection framework
# or FastAPI's `app.state`.

config_manager: ConfigManager = None
db_manager: DatabaseManager = None
logger: logging.Logger = None

def initialize_dependencies():
    """
    Initializes the shared components (config, db, logger) that the API endpoints will need.
    This should be called once at application startup.
    """
    global config_manager, db_manager, logger

    # Set up logger
    # In a real scenario, this would be configured more robustly, but for now,
    # we'll use a basic configuration.
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("api")

    # Initialize ConfigManager
    config_path = Path("/config/config.toml") # Using the default path
    config_manager = ConfigManager(config_path=config_path)

    # Initialize DatabaseManager
    db_path = config_manager.get_path("database_file")
    db_manager = DatabaseManager(db_path=db_path)
    db_manager.connect()

def get_db():
    """FastAPI dependency to get the database manager."""
    return db_manager