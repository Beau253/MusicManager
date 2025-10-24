# src/music_manager/core/__init__.py

"""
MusicManager Core Package
-------------------------

This package contains the foundational, self-contained components of the
MusicManager application.

These modules are the building blocks used by all other parts of the system,
such as the CLI and service-specific workflows. They are designed to be
independent of the application's higher-level logic.

Modules:
- config_manager: Handles loading and saving of the `config.toml` file.
- database_manager: Manages all interactions with the SQLite database.
- logger: Configures the application-wide logging system.
"""

# The __all__ variable defines the public API of this package.
# It makes it clear which classes are intended for use by other parts of
# the application.
__all__ = [
    "ConfigManager",
    "DatabaseManager",
    "setup_logging",
]