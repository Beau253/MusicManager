# src/music_manager/cli/plex_commands.py

import click
import logging

# -----------------------------------------------------------------------------
# Plex Command Group
# -----------------------------------------------------------------------------

@click.group(name="plex", help="Interact with your Plex Media Server.")
@click.pass_context
def plex_group(ctx):
    """
    A group of commands for managing and viewing your Plex instance.
    All commands require a valid Plex URL and Token to be configured.
    """
    plex_wrapper = ctx.obj.get('plex')
    if not plex_wrapper or not plex_wrapper.is_configured():
        click.echo("Error: Plex URL and/or Token are not configured. Please run the 'setup' command or edit your config file.")
        ctx.exit()

# --- Plex Sub-commands ---

@plex_group.command(name="status", help="Check the connection to the Plex server.")
@click.pass_context
def status_command(ctx):
    """
    Connects to the Plex server and displays its version and server information
    to verify that the connection and token are working correctly.
    """
    logger = ctx.obj['logger']
    plex_wrapper = ctx.obj['plex']
    
    logger.info("Checking Plex server status...")
    click.echo("Connecting to Plex server...")
    
    plex_server = plex_wrapper.get_server_instance()
    
    if plex_server:
        click.secho("Successfully connected to Plex!", fg="green")
        click.echo(f"  Server Name: {plex_server.friendlyName}")
        click.echo(f"  Version: {plex_server.version}")
        click.echo(f"  Platform: {plex_server.platform} ({plex_server.platformVersion})")
    else:
        logger.error("Failed to connect to Plex. Please check URL, Token, and network connectivity.")
        click.secho("Connection to Plex failed. Check logs for details.", fg="red")

@plex_group.command(name="scan-library", help="Trigger a scan of the music library in Plex.")
@click.option("--deep", is_flag=True, help="Perform a deep scan to force metadata refresh.")
@click.pass_context
def scan_library_command(ctx, deep):
    """
    Initiates a library scan for the configured music library in Plex.
    """
    logger = ctx.obj['logger']
    plex_wrapper = ctx.obj['plex']
    
    library_name = plex_wrapper.config_manager.get_plex_setting("library_name")
    
    logger.info(f"Triggering a {'deep' if deep else 'standard'} scan for Plex library: '{library_name}'")
    click.echo(f"Sending scan command to Plex for library '{library_name}'...")
    
    success = plex_wrapper.scan_library(deep_scan=deep)
    
    if success:
        click.secho("Successfully initiated library scan.", fg="green")
    else:
        click.secho("Failed to initiate library scan. The library name may be incorrect or the server may be busy.", fg="red")

@plex_group.command(name="empty-trash", help="Empty the trash for the music library.")
@click.confirmation_option(prompt="Are you sure you want to empty the trash in Plex? This permanently removes deleted media.")
@click.pass_context
def empty_trash_command(ctx):
    """
    Empties the trash for the configured music library, which permanently
    deletes metadata for media that is no longer available at its scanned path.
    """
    logger = ctx.obj['logger']
    plex_wrapper = ctx.obj['plex']
    
    library_name = plex_wrapper.config_manager.get_plex_setting("library_name")
    
    logger.info(f"Triggering 'Empty Trash' for Plex library: '{library_name}'")
    click.echo(f"Sending 'Empty Trash' command to Plex...")
    
    success = plex_wrapper.empty_trash()
    
    if success:
        click.secho("Successfully initiated 'Empty Trash' operation.", fg="green")
    else:
        click.secho("Failed to empty trash. Check logs for details.", fg="red")

@plex_group.command(name="sync-playlist", help="Create or update a native Plex playlist from a Spotify URL.")
@click.argument("spotify_playlist_url")
@click.pass_context
def sync_playlist_command(ctx, spotify_playlist_url):
    """
    Fetches a Spotify playlist, finds all corresponding tracks in your Plex
    library (using the local MusicManager DB as a map), and creates or
    updates a native Plex playlist with the same name.
    """
    logger = ctx.obj['logger']
    plex_wrapper = ctx.obj['plex']
    spotify_wrapper = ctx.obj['spotify']
    db_manager = ctx.obj['db']
    
    click.echo(f"Starting native Plex playlist sync for: {spotify_playlist_url}")
    
    # 1. Fetch playlist details from Spotify
    logger.info("Fetching playlist tracks from Spotify...")
    playlist_name, tracks = spotify_wrapper.get_playlist_tracks(spotify_playlist_url)
    if not playlist_name:
        click.secho("Failed to fetch playlist from Spotify. Please check the URL and your credentials.", fg="red")
        return
        
    click.echo(f"Found {len(tracks)} tracks in Spotify playlist '{playlist_name}'.")
    
    # 2. Map Spotify tracks to Plex tracks via our local database
    logger.info("Mapping Spotify tracks to local files via the database...")
    track_uris = [track['uri'] for track in tracks]
    plex_track_objects = plex_wrapper.find_plex_tracks_for_spotify_uris(db_manager, track_uris)
    
    click.echo(f"Successfully mapped {len(plex_track_objects)} tracks to your Plex library.")
    
    # 3. Create or update the playlist in Plex
    logger.info(f"Creating/updating native Plex playlist '{playlist_name}'...")
    success = plex_wrapper.create_or_update_playlist(playlist_name, plex_track_objects)
    
    if success:
        click.secho(f"Successfully synced playlist '{playlist_name}' to Plex!", fg="green")
    else:
        click.secho(f"Failed to sync playlist '{playlist_name}' to Plex. Check logs for details.", fg="red")

@plex_group.command(name="verify-tracks", help="Check which organized tracks are missing from Plex.")
@click.pass_context
def verify_tracks_command(ctx):
    """
    Compares the local database against the Plex library to find tracks that
    are marked as 'organized' but have not been successfully scanned into Plex.
    """
    logger = ctx.obj['logger']
    plex_wrapper = ctx.obj['plex']
    db_manager = ctx.obj['db']
    
    click.echo("Verifying local database against Plex library... (this may take a moment)")
    
    missing_tracks = plex_wrapper.find_missing_tracks(db_manager)
    
    if missing_tracks is None:
        click.echo("An error occurred during verification. Check logs.")
        return
        
    if not missing_tracks:
        click.secho("Verification complete. All organized tracks are present in Plex!", fg="green")
        return
        
    click.secho(f"Found {len(missing_tracks)} tracks that are organized but missing from Plex:", fg="yellow")
    click.echo("This may indicate a Plex scan is needed or there is a path mapping issue.")
    
    missing_lines = [
        f"{track.get('artist', 'N/A')} - {track.get('title', 'N/A')} (Path: {track.get('local_path', 'N/A')})"
        for track in missing_tracks
    ]
    
    click.echo_via_pager("\n".join(missing_lines))