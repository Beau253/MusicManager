# src/music_manager/cli/library_commands.py

import click
import logging

# Assume workflow functions will be defined in a dedicated module
# from music_manager.workflows.library_workflow import run_library_scan, run_picard_processing

# -----------------------------------------------------------------------------
# Library Command Group
# -----------------------------------------------------------------------------

@click.group(name="library", help="Manage the organized music library and its metadata.")
@click.pass_context
def library_group(ctx):
    """
    A group of commands for interacting with the final organized music library,
    including scanning, metadata processing, and searching.
    """
    pass

# --- Library Sub-commands ---

@library_group.command(name="scan", help="Scan the library to find and catalog untracked files.")
@click.option("--full", is_flag=True, help="Perform a full metadata refresh on ALL files, not just untracked ones.")
@click.pass_context
def scan_command(ctx, full):
    """
    Scans the organized music library directory.

    Default behavior is to find local audio files that are not yet tracked in
    the database, identify them using MusicBrainz/Picard, and add them.

    The --full flag forces a re-scan and metadata update for every single file
    in the library, which can take a very long time.
    """
    logger = ctx.obj['logger']
    
    if full:
        logger.info("Starting a FULL library scan and metadata refresh...")
        click.confirm("This will re-process every file in your library to refresh its metadata from MusicBrainz. This can take a very long time. Are you sure you want to continue?", abort=True)
    else:
        logger.info("Starting a scan for untracked files in the library...")
    
    try:
        # This function would contain the core logic from the blueprint:
        # 1. Recursively find all audio files in the library directory.
        # 2. For each file, check if its path exists in the database.
        # 3. If not (or if --full is used), call the organizer service (Picard).
        # 4. Read the new tags and update/insert into the DB.
        # run_library_scan(ctx.obj['db'], ctx.obj['config'], full_rescan=full)
        
        # Placeholder for now:
        click.echo("---")
        click.echo(f"CONCEPT: This command would scan the organized music directory {'(full rescan)' if full else ''}:")
        click.echo("1. Find all audio files.")
        click.echo("2. For each untracked file, call the Picard organizer service.")
        click.echo("3. Read the authoritative MusicBrainz tags written by Picard.")
        click.echo("4. Populate the 'tracks' and 'metadata' tables in the database.")
        click.echo("---")
        
        logger.info("Library scan complete.")
        
    except Exception as e:
        logger.error(f"A critical error occurred during the library scan: {e}", exc_info=True)
        click.echo("An error occurred during the scan. Please check the logs.")

@library_group.command(name="process-metadata", help="Run Picard on all newly downloaded files.")
@click.pass_context
def process_metadata_command(ctx):
    """
    Finds all tracks with status 'download_complete' and processes them
    with the organizer service (Picard) to enrich metadata and move them
    to the final library location.
    """
    logger = ctx.obj['logger']
    logger.info("Starting metadata processing for newly downloaded files...")
    
    try:
        # This function would be the core Picard workflow.
        # run_picard_processing(ctx.obj['db'], ctx.obj['config'])
        
        # Placeholder for now:
        click.echo("---")
        click.echo("CONCEPT: This command would:")
        click.echo("1. Query the database for all tracks with 'download_complete' status.")
        click.echo("2. For each track, call the Picard organizer service.")
        click.echo("3. After Picard moves the file, update the track's status to 'organized'.")
        click.echo("4. Populate the 'metadata' table with the rich data from the file.")
        click.echo("---")
        
        logger.info("Metadata processing complete.")
        
    except Exception as e:
        logger.error(f"A critical error occurred during metadata processing: {e}", exc_info=True)
        click.echo("An error occurred. Please check the logs.")
        
@library_group.command(name="search", help="Search the library's metadata.")
@click.argument("query")
@click.pass_context
def search_command(ctx, query):
    """
    Performs a search against the 'metadata' table for matching artists,
    albums, or track titles.
    """
    logger = ctx.obj['logger']
    db_manager = ctx.obj['db']
    
    logger.info(f"Searching library metadata for: '{query}'")
    try:
        # This assumes the db_manager has a method to search the metadata table
        results = db_manager.search_metadata(query=query)
        
        if not results:
            click.echo(f"No results found in the library for '{query}'.")
            return
            
        click.secho(f"--- Library Search Results ({len(results)}) ---", fg="cyan", bold=True)
        
        result_lines = [
            f"{track.get('artist', 'N/A')} - {track.get('album', 'N/A')} - {track.get('title', 'N/A')}"
            for track in results
        ]
        
        click.echo_via_pager("\n".join(result_lines))
        
    except Exception as e:
        logger.error(f"An error occurred during the library search: {e}", exc_info=True)
        click.echo("An error occurred during the search. Please check the logs.")

@library_group.command(name="stats", help="Display statistics about the music library.")
@click.pass_context
def stats_command(ctx):
    """
    Shows high-level statistics about the organized music library based on
    the data stored in the database.
    """
    logger = ctx.obj['logger']
    db_manager = ctx.obj['db']
    
    try:
        # These would be new methods in the DatabaseManager
        total_tracks = db_manager.get_metadata_count()
        total_artists = db_manager.get_distinct_artist_count()
        total_albums = db_manager.get_distinct_album_count()
        total_size_gb = db_manager.get_total_library_size_gb()
        
        click.secho("--- Music Library Statistics ---", fg="cyan", bold=True)
        click.echo(f"{'Total Tracks':<20}: {total_tracks}")
        click.echo(f"{'Unique Artists':<20}: {total_artists}")
        click.echo(f"{'Unique Albums':<20}: {total_albums}")
        click.echo(f"{'Total Library Size':<20}: {total_size_gb:.2f} GB")
        
    except Exception as e:
        logger.error(f"An error occurred while calculating library stats: {e}", exc_info=True)
        click.echo("An error occurred. Please check the logs.")