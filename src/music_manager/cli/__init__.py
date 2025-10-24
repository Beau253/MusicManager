# src/music_manager/cli/__init__.py

"""
MusicManager CLI Package
------------------------

This package contains all the modules that define the hierarchical command-line
interface for the MusicManager application, built using the 'click' library.

Each module within this package is responsible for a specific group of commands,
such as 'db', 'plex', 'lidarr', etc. These command groups are then imported and
registered into the main CLI application in `music_manager.main`.

This modular approach keeps the main entry point clean and makes the CLI
easily extensible.
"""

# The __all__ variable defines the public API of this package.
# When a module does `from music_manager.cli import *`, only these names
# will be imported. This is a best practice for package organization.
__all__ = [
    "db_group",
    "downloader_group",
    "library_group",
    "lidarr_group",
    "plex_group",
    "settings_group",
    "spotify_group",
    "support_command",
]