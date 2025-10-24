# src/music_manager/cli/downloader_commands.py

import click
import logging

# Assume some high-level workflow functions will be defined in a 'workflows' module
# For now, we can conceptualize them here and import later.
# from music_manager.workflows.download_workflow import process_download_queue

# -----------------------------------------------------------------------------
# Downloader Command Group
# -----------------------------------------------------------------------------

@click.group(name="downloader", help="Manage the track acquisition and download queue.")
@click.pass_context
def downloader_group(ctx):
    """
    A group of commands for managing the track download queue and interacting
    with the downloader service ('onthespot').
    """
    pass

# --- Downloader Sub-commands ---

@downloader_group.command(name="process-queue", help="Download all queued tracks.")
@click.option("--limit", type=int, default=0, help="Limit the number of tracks to process in this run (0 for no limit, respects daily quota).")
@click.pass_context
def process_queue_command(ctx, limit):
    """
    Initiates the download process for all tracks currently in 'queued' status,
    respecting the daily API quota.
    """
    logger = ctx.obj['logger']
    
    logger.info("Manually starting the download queue processing...")
    click.echo("Starting download process for all queued tracks...")
    
    try:
        # This function would contain the core logic for fetching queued tracks from the DB,
        # checking the quota, and calling the downloader service for each one.
        # It should be defined in a higher-level 'services' or 'workflows' module.
        # process_download_queue(ctx.obj['db'], ctx.obj['config'], limit)
        
        # Placeholder for now:
        click.echo("---")
        click.echo("CONCEPT: This command would:")
        click.echo("1. Load the current daily quota usage.")
        click.echo("2. Query the database for all tracks with 'queued' status.")
        click.echo("3. Loop through tracks up to the daily limit (or the --limit flag).")
        click.echo("4. For each track, call the 'onthespot' downloader service.")
        click.echo("5. Update the database with 'download_complete' or 'download_failed'.")
        click.echo("---")
        logger.info("Download queue processing complete.")
        
    except Exception as e:
        logger.error(f"A critical error occurred during queue processing: {e}", exc_info=True)
        click.echo("An error occurred during the download process. Please check the logs.")

@downloader_group.command(name="view-queue", help="View all tracks waiting to be downloaded.")
@click.pass_context
def view_queue_command(ctx):
    """
    Displays a list of all tracks currently in the download queue ('queued' status).
    """
    logger = ctx.obj['logger']
    db_manager = ctx.obj['db']
    
    try:
        queued_tracks = db_manager.search_tracks(status='queued')
        
        if not queued_tracks:
            click.echo("The download queue is currently empty.")
            return

        click.secho(f"--- Download Queue ({len(queued_tracks)} Tracks) ---", fg="cyan", bold=True)
        
        track_lines = [
            f"{track.get('artist_name_spotify', 'N/A')} - {track.get('track_name_spotify', 'N/A')} (Added: {track.get('added_date', 'N/A')})"
            for track in queued_tracks
        ]
        
        click.echo_via_pager("\n".join(track_lines))

    except Exception as e:
        logger.error(f"Failed to query the download queue: {e}", exc_info=True)
        click.echo("An error occurred while fetching the queue. Check logs for details.")
        
@downloader_group.command(name="view-failed", help="View all tracks that failed to download.")
@click.pass_context
def view_failed_command(ctx):
    """
    Displays a list of all tracks that are marked with a 'failed' status,
    along with their last error message.
    """
    logger = ctx.obj['logger']
    db_manager = ctx.obj['db']
    
    try:
        failed_tracks = db_manager.search_tracks(status='download_failed')
        
        if not failed_tracks:
            click.echo("No failed downloads found.")
            return

        click.secho(f"--- Failed Downloads ({len(failed_tracks)} Tracks) ---", fg="red", bold=True)
        
        for track in failed_tracks:
            click.echo(
                f"Track: {track.get('artist_name_spotify', 'N/A')} - {track.get('track_name_spotify', 'N/A')}\n"
                f"  -> Last Attempt: {track.get('last_attempt_date', 'N/A')}\n"
                f"  -> Fail Count: {track.get('fail_count', 'N/A')}\n"
                f"  -> Error: {track.get('error_message', 'No error message recorded.')}\n"
            )

    except Exception as e:
        logger.error(f"Failed to query failed downloads: {e}", exc_info=True)
        click.echo("An error occurred while fetching failed downloads. Check logs for details.")

@downloader_group.command(name="quota-status", help="Check the current API download quota usage.")
@click.pass_context
def quota_status_command(ctx):
    """
    Checks and displays the current usage against the daily download quota.
    """
    logger = ctx.obj['logger']
    
    try:
        # The quota logic would be managed by a dedicated class or functions
        # that read/write to the onthespot_quota.json file.
        # from music_manager.services.quota_manager import get_quota_status
        
        # Placeholder for now:
        # quota_usage, quota_limit = get_quota_status(ctx.obj['config'])
        quota_usage = 10 # dummy data
        quota_limit = 75 # dummy data
        
        click.echo("--- Daily Download Quota Status ---")
        click.echo(f"Usage Today: {quota_usage} / {quota_limit} tracks")
        
        remaining = quota_limit - quota_usage
        if remaining > 0:
            click.secho(f"{remaining} downloads remaining today.", fg="green")
        else:
            click.secho("Quota limit reached for today.", fg="yellow")

    except Exception as e:
        logger.error(f"Failed to check quota status: {e}", exc_info=True)
        click.echo("An error occurred while checking quota status. Check logs for details.")