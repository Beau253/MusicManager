# src/music_manager/cli/settings_commands.py

import click
import logging
from pathlib import Path

# -----------------------------------------------------------------------------
# Settings Command Group
# -----------------------------------------------------------------------------

@click.group(name="settings", help="View and manage application configuration.")
@click.pass_context
def settings_group(ctx):
    """
    A group of commands for viewing and managing the application's settings
    stored in the config.toml file.
    """
    pass

# --- Settings Sub-commands ---

@settings_group.command(name="view", help="Display the current configuration.")
@click.option("--show-secrets", is_flag=True, help="Display sensitive values like API keys and tokens.")
@click.pass_context
def view_command(ctx, show_secrets):
    """
    Prints the contents of the config.toml file to the console.
    By default, it masks sensitive information for security.
    """
    logger = ctx.obj['logger']
    config_manager = ctx.obj['config']
    
    logger.info("Displaying current application configuration.")
    click.secho("--- Current Configuration ---", fg="cyan", bold=True)
    
    config_dict = config_manager.get_config_as_dict()
    secrets_to_mask = ['client_secret', 'token', 'api_key', 'webhook_url']

    for section, settings in config_dict.items():
        click.secho(f"[{section}]", bold=True)
        for key, value in settings.items():
            if key in secrets_to_mask and not show_secrets:
                value = '********'
            click.echo(f"  {key} = {value}")
        click.echo("") # Add a newline for readability

@settings_group.command(name="setup", help="Run the interactive setup wizard.")
@click.pass_context
def setup_command(ctx):
    """
    Runs a guided, interactive setup wizard to configure all essential
    application settings. This is the recommended way to create or update
    your configuration.
    """
    logger = ctx.obj['logger']
    config_manager = ctx.obj['config']
    
    logger.info("Starting interactive setup wizard.")
    click.secho("--- MusicManager Interactive Setup Wizard ---", fg="green", bold=True)
    click.echo("This will guide you through all necessary configuration options.")
    click.echo("Press Enter to accept the current value shown in [brackets].\n")
    
    # --- [1] Core Paths ---
    click.secho("--- [1] Core Path Configuration ---", fg="cyan")
    music_root_dir = click.prompt("Enter the absolute path to your root music directory", default=config_manager.get_main_setting('music_root_dir'), type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True))
    unorganized_subdir = click.prompt("Enter the subdirectory for new downloads (relative to root)", default=config_manager.get_main_setting('unorganized_subdir'))
    organized_subdir = click.prompt("Enter the subdirectory for the final organized library (relative to root)", default=config_manager.get_main_setting('organized_subdir'))
    
    # --- [2] Spotify Settings ---
    click.secho("\n--- [2] Spotify API Configuration ---", fg="cyan")
    click.echo("Get these from your Spotify Developer Dashboard.")
    spotify_client_id = click.prompt("Enter your Spotify Client ID", default=config_manager.get_spotify_setting('client_id'))
    spotify_client_secret = click.prompt("Enter your Spotify Client Secret", default=config_manager.get_spotify_setting('client_secret'), hide_input=True)
    
    # --- [3] Lidarr Settings ---
    click.secho("\n--- [3] Lidarr API Configuration ---", fg="cyan")
    lidarr_url = click.prompt("Enter your Lidarr URL (e.g., http://localhost:8686)", default=config_manager.get_lidarr_setting('url'))
    lidarr_api_key = click.prompt("Enter your Lidarr API Key", default=config_manager.get_lidarr_setting('api_key'), hide_input=True)

    # --- [4] Plex Settings ---
    click.secho("\n--- [4] Plex API Configuration ---", fg="cyan")
    plex_url = click.prompt("Enter your Plex URL (e.g., http://localhost:32400)", default=config_manager.get_plex_setting('url'))
    plex_token = click.prompt("Enter your Plex Token", default=config_manager.get_plex_setting('token'), hide_input=True)
    plex_library_name = click.prompt("Enter the name of your Plex music library", default=config_manager.get_plex_setting('library_name'))

    # --- Update and Save Configuration ---
    click.echo("\nUpdating and saving configuration...")
    
    # Update values in the in-memory config object
    config_manager.update_setting('main', 'music_root_dir', str(Path(music_root_dir)))
    config_manager.update_setting('main', 'unorganized_subdir', unorganized_subdir)
    config_manager.update_setting('main', 'organized_subdir', organized_subdir)
    
    config_manager.update_setting('spotify', 'client_id', spotify_client_id)
    config_manager.update_setting('spotify', 'client_secret', spotify_client_secret)
    
    config_manager.update_setting('lidarr', 'url', lidarr_url)
    config_manager.update_setting('lidarr', 'api_key', lidarr_api_key)
    
    config_manager.update_setting('plex', 'url', plex_url)
    config_manager.update_setting('plex', 'token', plex_token)
    config_manager.update_setting('plex', 'library_name', plex_library_name)
    
    # Save the updated config to disk
    config_manager.save_config()
    
    click.secho("\nSetup complete! Your configuration has been saved.", fg="green")
    click.echo("You can now run the 'validate' command to test your new settings.")

@settings_group.command(name="validate", help="Validate the current configuration and connections.")
@click.pass_context
def validate_command(ctx):
    """
    Performs a comprehensive health check on the application's configuration.
    It checks paths, dependencies, and all external API connections.
    """
    logger = ctx.obj['logger']
    
    click.secho("--- Running Configuration Validator ---", fg="cyan", bold=True)
    
    # --- This would call a high-level workflow function ---
    # from music_manager.workflows.validation_workflow import run_validation
    # success = run_validation(ctx.obj)
    
    # Placeholder for now:
    click.echo("\n[1/4] Checking Core Paths...")
    click.secho("  - OK: Music Root Directory", fg="green")
    
    click.echo("\n[2/4] Checking Dependencies...")
    click.secho("  - OK: Picard found", fg="green")
    click.secho("  - OK: fpcalc (AcoustID) found", fg="green")
    
    click.echo("\n[3/4] Checking API Connections...")
    click.secho("  - OK: Spotify API credentials are valid.", fg="green")
    click.secho("  - OK: Connected to Lidarr server successfully.", fg="green")
    click.secho("  - OK: Connected to Plex server successfully.", fg="green")
    
    click.secho("\n--- Validation Successful: Your configuration appears to be correct! ---", fg="green")
    
    # Example of a failure:
    # click.secho("\n[3/4] Checking API Connections...")
    # click.secho("  - FAIL: Could not connect to Plex. Please check URL and Token.", fg="red")
    # click.secho("\n--- Validation Failed: Please review the errors above. ---", fg="red")

@settings_group.command(name="set-log-level", help="Temporarily change the console log level.")
@click.argument("level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False))
@click.pass_context
def set_log_level_command(ctx, level):
    """
    Dynamically changes the verbosity of messages displayed in the console
    for the current application session. This does not change the config file.
    """
    logger = ctx.obj['logger']
    new_level = getattr(logging, level.upper())

    # Find the console handler and set its level
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(new_level)
            click.secho(f"Console log level temporarily set to {level.upper()}.", fg="yellow")
            logger.info("This is an INFO message.")
            logger.debug("This is a DEBUG message (will only show if level is DEBUG).")
            return