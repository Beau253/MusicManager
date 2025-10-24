# src/music_manager/main.py

import click
from dotenv import load_dotenv

# --- Load Environment Variables ---
# This is the first action, loading variables from a .env file.
# This makes them available for all subsequent modules, especially the ConfigManager.
# It will NOT overwrite existing environment variables, making it safe for production.
load_dotenv()

# --- Core Application Imports ---
from music_manager import __version__
from music_manager.core.config_manager import ConfigManager
from music_manager.core.database_manager import DatabaseManager
from music_manager.core.logger import setup_logging

# --- Wrapper Imports for Context ---
from music_manager.wrappers.spotify_wrapper import SpotifyWrapper
from music_manager.wrappers.plex_wrapper import PlexWrapper
from music_manager.wrappers.lidarr_wrapper import LidarrWrapper

# --- CLI Command Group Imports ---
from music_manager.cli.db_commands import db_group
from music_manager.cli.downloader_commands import downloader_group
from music_manager.cli.library_commands import library_group
from music_manager.cli.lidarr_commands import lidarr_group
from music_manager.cli.plex_commands import plex_group
from music_manager.cli.settings_commands import settings_group
from music_manager.cli.spotify_commands import spotify_group
from music_manager.cli.support_commands import support_command

# -----------------------------------------------------------------------------
# Main CLI Group
# -----------------------------------------------------------------------------

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(__version__, '-v', '--version', message='%(prog)s, version %(version)s')
@click.pass_context
def cli(ctx):
    """
    MusicManager: The central brain for your automated music library.

    This is the main entry point for the application's command-line interface.
    It initializes and provides core components like the configuration manager,
    database, and logger to all sub-commands via the context object.
    """
    # Ensure the context object is a dictionary.
    ctx.ensure_object(dict)

    try:
        # --- 1. Initialize Configuration Manager ---
        # This is the first component to be initialized as it drives all other settings.
        config_manager = ConfigManager()
        ctx.obj['config'] = config_manager

        # --- 2. Initialize Logging ---
        # The logger is configured based on settings from the ConfigManager.
        logger = setup_logging(
            log_level_console=config_manager.get_logging_setting("log_level_console"),
            log_level_file=config_manager.get_logging_setting("log_level_file")
        )
        ctx.obj['logger'] = logger

        # --- 3. Initialize Database Manager ---
        # The database path is retrieved from the config.
        db_manager = DatabaseManager(
            db_path=config_manager.get_path("database_file")
        )
        ctx.obj['db'] = db_manager
        
        # --- 4. Initialize API Wrappers ---
        # These wrappers are made available to any command that needs them.
        # They are initialized with the config manager to get their settings.
        ctx.obj['spotify'] = SpotifyWrapper(config_manager)
        ctx.obj['plex'] = PlexWrapper(config_manager)
        ctx.obj['lidarr'] = LidarrWrapper(config_manager)

    except Exception as e:
        # If a critical error happens during setup (e.g., can't write to log file),
        # print it and exit to prevent further issues.
        click.echo(f"FATAL: A critical error occurred during application initialization: {e}", err=True)
        # Using a distinct exit code for setup failure.
        exit(1)

# --- Register all command groups and standalone commands ---
cli.add_command(db_group)
cli.add_command(downloader_group)
cli.add_command(library_group)
cli.add_command(lidarr_group)
cli.add_command(plex_group)
cli.add_command(settings_group)
cli.add_command(spotify_group)
cli.add_command(support_command)

# -----------------------------------------------------------------------------
# Application Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # The 'obj={}' ensures that the context object is always created,
    # which is a best practice for 'click' applications.
    cli(obj={})