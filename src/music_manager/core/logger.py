# src/music_manager/core/logger.py

import logging
import logging.handlers
import sys
from pathlib import Path
import click

# Use platformdirs to find the appropriate log directory for the OS
import platformdirs

# Define application constants for platformdirs
APP_NAME = "MusicManager"
APP_AUTHOR = "MusicManager" # Or your author/org name

class ClickColorHandler(logging.StreamHandler):
    """
    A logging handler that uses click.secho for colored console output.
    This enhances readability by color-coding log levels.
    """
    _level_colors = {
        logging.CRITICAL: "magenta",
        logging.ERROR: "red",
        logging.WARNING: "yellow",
        logging.INFO: "green",
        logging.DEBUG: "blue",
    }

    def emit(self, record):
        # A handler's level filtering is done by comparing the record's level
        # to the handler's level before this method is even called.
        try:
            msg = self.format(record)
            # Use click.secho for colored output. All logs go to stderr by convention.
            fg_color = self._level_colors.get(record.levelno, "white")
            click.secho(msg, fg=fg_color, err=True)
        except Exception:
            self.handleError(record)

def setup_logging(log_level_console: str = "INFO", log_level_file: str = "DEBUG") -> logging.Logger:
    """
    Configures and returns the root logger for the application.

    This setup directs logs to two destinations (handlers):
    1. Console (StreamHandler): For immediate, colored feedback to the user.
    2. File (RotatingFileHandler): For a persistent, detailed record for debugging.

    Args:
        log_level_console: The minimum level for logs to display on the console.
        log_level_file: The minimum level for logs to be saved to the file.

    Returns:
        The configured root logger instance for the application.
    """
    # Get the application's root logger. All other loggers will inherit from this.
    # Using a named logger avoids interfering with other libraries' logging.
    app_logger = logging.getLogger("music_manager")
    
    # Set the logger's base level to DEBUG. This allows it to pass all messages;
    # the handlers will then filter based on their own configured levels.
    app_logger.setLevel(logging.DEBUG)
    
    # Prevent the logger from propagating messages to the absolute root logger,
    # which might have its own handlers (e.g., from other libraries).
    app_logger.propagate = False
    
    # If handlers are already configured (e.g., from a previous call), clear them
    # to avoid duplicate log messages.
    if app_logger.hasHandlers():
        app_logger.handlers.clear()

    # --- Console Handler (for user-facing output) ---
    console_handler = ClickColorHandler()
    
    # Set the level for console output from the configuration.
    console_level = getattr(logging, log_level_console.upper(), logging.INFO)
    console_handler.setLevel(console_level)
    
    # Use a simple formatter for console messages for better readability.
    console_formatter = logging.Formatter(
        "%(levelname)-8s :: %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    app_logger.addHandler(console_handler)

    # --- File Handler (for persistent, detailed logs) ---
    try:
        # Use platformdirs to find the correct, OS-specific log directory.
        log_dir = Path(platformdirs.user_log_dir(APP_NAME, APP_AUTHOR))
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = log_dir / "music_manager.log"

        # Set the level for file output from the configuration.
        file_level = getattr(logging, log_level_file.upper(), logging.DEBUG)
        
        # Use a rotating file handler to prevent log files from growing indefinitely.
        # It will keep 5 backup logs of 10MB each.
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(file_level)
        
        # Use a more detailed formatter for the file log.
        file_formatter = logging.Formatter(
            "%(asctime)s [%(name)s:%(lineno)d] [%(levelname)-8s] - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        app_logger.addHandler(file_handler)
        
        # Log the location of the log file for user convenience.
        app_logger.debug(f"Logging initialized. Detailed logs will be saved to: {log_file_path}")

    except Exception as e:
        # If file logging fails, log a critical error to the console.
        app_logger.critical(f"Failed to initialize file logger: {e}", exc_info=True)

    return app_logger