# src/music_manager/cli/lidarr_commands.py

import click
import logging

# -----------------------------------------------------------------------------
# Lidarr Command Group
# -----------------------------------------------------------------------------

@click.group(name="lidarr", help="Interact with your Lidarr instance.")
@click.pass_context
def lidarr_group(ctx):
    """
    A group of commands for managing and viewing your Lidarr instance.
    All commands require a valid Lidarr URL and API Key to be configured.
    """
    # Check if Lidarr is configured before allowing any sub-command to run.
    lidarr_wrapper = ctx.obj.get('lidarr')
    if not lidarr_wrapper or not lidarr_wrapper.is_configured():
        click.echo("Error: Lidarr URL and/or API Key are not configured. Please run the 'setup' command or edit your config file.")
        # Exit the command group context if not configured.
        ctx.exit()

# --- Lidarr Sub-commands ---

@lidarr_group.command(name="status", help="Check the connection to the Lidarr server.")
@click.pass_context
def status_command(ctx):
    """
    Pings the Lidarr server and displays its version information to verify
    that the connection and API key are working correctly.
    """
    logger = ctx.obj['logger']
    lidarr_wrapper = ctx.obj['lidarr']
    
    logger.info("Checking Lidarr server status...")
    click.echo("Pinging Lidarr server...")
    
    status_info = lidarr_wrapper.get_system_status()
    
    if status_info:
        click.secho("Successfully connected to Lidarr!", fg="green")
        click.echo(f"  Version: {status_info.get('version', 'N/A')}")
        click.echo(f"  Branch: {status_info.get('branch', 'N/A')}")
        click.echo(f"  Start Time: {status_info.get('startTime', 'N/A')}")
    else:
        logger.error("Failed to connect to Lidarr. Please check URL, API key, and network connectivity.")
        click.secho("Connection to Lidarr failed. Check logs for details.", fg="red")

@lidarr_group.command(name="view-queue", help="View the current download queue in Lidarr.")
@click.pass_context
def view_queue_command(ctx):
    """
    Fetches and displays the current list of items in Lidarr's download queue.
    """
    logger = ctx.obj['logger']
    lidarr_wrapper = ctx.obj['lidarr']
    
    logger.info("Fetching Lidarr download queue...")
    queue = lidarr_wrapper.get_queue()
    
    if queue is None:
        click.echo("An error occurred while fetching the Lidarr queue.")
        return
        
    if not queue:
        click.echo("Lidarr download queue is empty.")
        return
        
    click.secho(f"--- Lidarr Download Queue ({len(queue)} Items) ---", fg="cyan", bold=True)
    for item in queue:
        artist = item.get('artist', {}).get('artistName', 'N/A')
        album = item.get('album', {}).get('title', 'N/A')
        size_gb = item.get('size', 0) / (1024**3)
        progress = item.get('sizeleft', 0) / item.get('size', 1) * 100
        status = item.get('status', 'N/A')
        
        click.echo(f"[{status}] {artist} - {album}")
        click.echo(f"  -> Size: {size_gb:.2f} GB | Progress: {100 - progress:.1f}%")

@lidarr_group.command(name="add-artist", help="Add and monitor a new artist in Lidarr.")
@click.argument("artist_name")
@click.option("--no-search", is_flag=True, help="Add the artist but do not trigger a search for missing albums.")
@click.pass_context
def add_artist_command(ctx, artist_name, no_search):
    """
    Searches for an artist by name, and if found, adds them to Lidarr
    and begins monitoring them for new albums.
    """
    logger = ctx.obj['logger']
    lidarr_wrapper = ctx.obj['lidarr']
    
    logger.info(f"Attempting to add artist '{artist_name}' to Lidarr...")
    
    success = lidarr_wrapper.add_artist(artist_name=artist_name, search_for_missing_albums=not no_search)
    
    if success:
        click.secho(f"Successfully added and began monitoring '{artist_name}' in Lidarr.", fg="green")
    else:
        click.secho(f"Failed to add '{artist_name}' to Lidarr. Check logs for details.", fg="red")

@lidarr_group.command(name="refresh-artist", help="Trigger a refresh and rescan for an artist.")
@click.argument("artist_name")
@click.pass_context
def refresh_artist_command(ctx, artist_name):
    """
    Finds an existing artist in Lidarr and triggers the 'RefreshArtist' command,
    which rescans their discography and folder.
    """
    logger = ctx.obj['logger']
    lidarr_wrapper = ctx.obj['lidarr']
    
    logger.info(f"Attempting to refresh artist '{artist_name}' in Lidarr...")
    
    success = lidarr_wrapper.trigger_artist_refresh(artist_name=artist_name)
    
    if success:
        click.secho(f"Successfully triggered a refresh for '{artist_name}'.", fg="green")
    else:
        click.secho(f"Failed to refresh '{artist_name}'. They may not exist in Lidarr.", fg="red")

@lidarr_group.command(name="list-artists", help="List all artists currently monitored by Lidarr.")
@click.argument("filter_term", required=False)
@click.pass_context
def list_artists_command(ctx, filter_term):
    """
    Retrieves and lists all artists from Lidarr. Can be filtered with a search term.
    """
    logger = ctx.obj['logger']
    lidarr_wrapper = ctx.obj['lidarr']
    
    logger.info("Fetching all artists from Lidarr...")
    artists = lidarr_wrapper.get_all_artists()
    
    if artists is None:
        click.echo("An error occurred while fetching artists.")
        return
        
    if filter_term:
        artists = [artist for artist in artists if filter_term.lower() in artist.get('artistName', '').lower()]

    if not artists:
        click.echo("No artists found in Lidarr" + (f" matching '{filter_term}'." if filter_term else "."))
        return
        
    click.secho(f"--- Monitored Artists ({len(artists)}) ---", fg="cyan", bold=True)
    
    artist_lines = [
        f"{artist.get('artistName', 'N/A')} (Status: {'Monitored' if artist.get('monitored') else 'Unmonitored'})"
        for artist in artists
    ]
    
    click.echo_via_pager("\n".join(artist_lines))