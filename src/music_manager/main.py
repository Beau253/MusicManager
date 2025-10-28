# src/music_manager/main.py

import click
from dotenv import load_dotenv

# --- Load Environment Variables ---
# This is the first action, loading variables from a .env file.
# This makes them available for all subsequent modules, especially the ConfigManager.
# It will NOT overwrite existing environment variables, making it safe for production.
load_dotenv()

# --- Core Application Imports ---
from music_manager.core.app_factory import create_app_context

# --- CLI Command Group Imports ---
from music_manager.cli.db_commands import db_group
from music_manager.cli.downloader_commands import downloader_group
from music_manager.cli.library_commands import library_group
from music_manager.cli.lidarr_commands import lidarr_group
from music_manager.cli.plex_commands import plex_group
from music_manager.cli.settings_commands import settings_group
from music_manager.cli.spotify_commands import spotify_group
from music_manager.cli.support_commands import support_command
from music_manager import __version__

# -----------------------------------------------------------------------------
# API Server Command
# -----------------------------------------------------------------------------

@click.command()
@click.option('--host', default='0.0.0.0', help='The host to bind to.')
@click.option('--port', default=8000, type=int, help='The port to run on.')
def api(host, port):
    """Launch the MusicManager REST API server."""
    click.echo(f"Starting MusicManager API server on http://{host}:{port}")
    import uvicorn
    uvicorn.run("music_manager.api.main:app", host=host, port=port, reload=False)

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
    # Use the central factory to create the application context.
    # This ensures all core components are initialized consistently.
    ctx.obj = create_app_context()
    

# --- Register all command groups and standalone commands ---
cli.add_command(db_group)
cli.add_command(downloader_group)
cli.add_command(library_group)
cli.add_command(lidarr_group)
cli.add_command(plex_group)
cli.add_command(settings_group)
cli.add_command(spotify_group)
cli.add_command(support_command)
cli.add_command(api)

# -----------------------------------------------------------------------------
# Application Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # The 'obj={}' ensures that the context object is always created,
    # which is a best practice for 'click' applications.
    cli(obj={})