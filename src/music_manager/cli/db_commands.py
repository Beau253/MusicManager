# src/music_manager/cli/db_commands.py

import click
import logging

# -----------------------------------------------------------------------------
# DB Command Group
# -----------------------------------------------------------------------------

@click.group(name="db", help="Perform low-level management of the application's database.")
@click.pass_context
def db_group(ctx):
    """
    A group of commands for direct interaction with the MusicManager database.
    Provides tools for viewing, searching, and manipulating track records.
    """
    # This function is the entry point for the 'db' command group.
    # The 'pass' statement means it does nothing on its own, but it allows
    # sub-commands to be attached to it. The context object (ctx) is implicitly
    # passed to all sub-commands.
    pass

# --- DB Sub-commands ---

@db_group.command(name="list", help="List tracks in the database. Supports searching.")
@click.argument("query", required=False)
@click.option("--status", help="Filter tracks by a specific status (e.g., queued, failed, organized).")
@click.pass_context
def list_command(ctx, query, status):
    """
    Lists tracks from the database. Can be filtered by a search query or status.
    """
    logger = ctx.obj['logger']
    db_manager = ctx.obj['db']
    
    logger.info(f"Querying database for tracks...")
    if query:
        logger.info(f"Applying search filter: '{query}'")
    if status:
        logger.info(f"Applying status filter: '{status}'")

    try:
        results = db_manager.search_tracks(query=query, status=status)
        
        if not results:
            click.echo("No tracks found matching the specified criteria.")
            return

        # Prepare a list of formatted strings for the pager
        track_lines = []
        for track in results:
            # Assuming the search_tracks method returns a dictionary or object
            # This needs to be adjusted to the actual return type of your db method
            line = (
                f"[{track.get('status', 'N/A'):<15}] "
                f"{track.get('artist', 'Unknown Artist')} - "
                f"{track.get('title', 'Unknown Title')} "
                f"(Spotify ID: {track.get('spotify_uri', 'N/A')})"
            )
            track_lines.append(line)

        click.echo(f"Found {len(track_lines)} track(s). Displaying results:")
        click.echo_via_pager("\n".join(track_lines))

    except Exception as e:
        logger.error(f"Failed to query the database: {e}", exc_info=True)
        click.echo("An error occurred while querying the database. Check logs for details.")

@db_group.command(name="info", help="Show detailed information for a specific track.")
@click.argument("spotify_uri")
@click.pass_context
def info_command(ctx, spotify_uri):
    """
    Displays all available information for a single track from the 'tracks'
    and 'metadata' tables using its Spotify URI.
    """
    logger = ctx.obj['logger']
    db_manager = ctx.obj['db']

    try:
        track_info = db_manager.get_track_details(spotify_uri=spotify_uri)

        if not track_info:
            logger.warning(f"No track found in the database with Spotify URI: {spotify_uri}")
            click.echo(f"Error: Track not found.")
            return
            
        click.secho(f"--- Detailed Info for Track: {spotify_uri} ---", fg="cyan", bold=True)
        for key, value in track_info.items():
            # Format keys to be more readable
            key_formatted = key.replace('_', ' ').title()
            click.echo(f"{key_formatted:>25}: {value or 'N/A'}")
        click.echo("-" * 50)

    except Exception as e:
        logger.error(f"Failed to retrieve details for track '{spotify_uri}': {e}", exc_info=True)
        click.echo("An error occurred. Check logs for details.")

@db_group.command(name="remove", help="Remove a track from the database.")
@click.argument("spotify_uri")
@click.confirmation_option(prompt="Are you sure you want to remove this track from the database? This may cause it to be re-downloaded.")
@click.pass_context
def remove_command(ctx, spotify_uri):
    """
    Removes a track's record from the database. Does not delete the audio file.
    This is useful for forcing a re-download or re-processing of a track.
    """
    logger = ctx.obj['logger']
    db_manager = ctx.obj['db']

    logger.info(f"Attempting to remove track '{spotify_uri}' from the database...")
    try:
        success = db_manager.remove_track(spotify_uri=spotify_uri)
        if success:
            logger.info(f"Successfully removed track '{spotify_uri}'.")
            click.echo(f"Track '{spotify_uri}' has been removed from the database.")
        else:
            logger.warning(f"Track '{spotify_uri}' was not found in the database.")
            click.echo(f"Error: Track not found.")
    except Exception as e:
        logger.error(f"An error occurred while removing track '{spotify_uri}': {e}", exc_info=True)
        click.echo("An error occurred. Check logs for details.")

@db_group.command(name="retry", help="Reset the status of failed tracks to be re-processed.")
@click.option("--all", "retry_all", is_flag=True, help="Retry all tracks with a 'failed' status.")
@click.argument("spotify_uri", required=False)
@click.pass_context
def retry_command(ctx, retry_all, spotify_uri):
    """
    Resets the status of one or all failed tracks back to 'queued',
    allowing the workflow to attempt processing them again.
    """
    logger = ctx.obj['logger']
    db_manager = ctx.obj['db']

    if not retry_all and not spotify_uri:
        click.echo("Error: You must specify a Spotify URI or use the --all flag.")
        return

    if retry_all and spotify_uri:
        click.echo("Error: You cannot specify a Spotify URI and use the --all flag at the same time.")
        return
        
    try:
        if retry_all:
            logger.info("Resetting all failed tracks to 'queued' status.")
            count = db_manager.reset_all_failed_tracks()
            click.echo(f"Successfully re-queued {count} failed track(s).")
        else:
            logger.info(f"Resetting track '{spotify_uri}' to 'queued' status.")
            success = db_manager.reset_track_status(spotify_uri=spotify_uri)
            if success:
                click.echo(f"Track '{spotify_uri}' has been re-queued for processing.")
            else:
                click.echo(f"Error: Could not find a failed track with URI '{spotify_uri}'.")

    except Exception as e:
        logger.error(f"An error occurred during the retry operation: {e}", exc_info=True)
        click.echo("An error occurred. Check logs for details.")