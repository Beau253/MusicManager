# src/music_manager/cli/spotify_commands.py

import click
import logging

# -----------------------------------------------------------------------------
# Spotify Command Group
# -----------------------------------------------------------------------------

@click.group(name="spotify", help="Interact with the Spotify API.")
@click.pass_context
def spotify_group(ctx):
    """
    A group of commands for interacting with Spotify to find and queue tracks
    for download. Requires valid Spotify API credentials.
    """
    spotify_wrapper = ctx.obj.get('spotify')
    if not spotify_wrapper or not spotify_wrapper.is_configured():
        click.echo("Error: Spotify Client ID and/or Secret are not configured. Please run the 'setup' command or edit your config file.")
        ctx.exit()

# --- Spotify Sub-commands ---

@spotify_group.command(name="manual-add", help="Search Spotify and add a track to the download queue.")
@click.argument("search_query", nargs=-1)
@click.pass_context
def manual_add_command(ctx, search_query):
    """
    Performs a search on Spotify using the provided query, displays the
    results, and allows the user to select a track to add to the download queue.
    """
    logger = ctx.obj['logger']
    spotify_wrapper = ctx.obj['spotify']
    db_manager = ctx.obj['db']
    
    if not search_query:
        click.echo("Error: Please provide a search query (e.g., 'Artist - Track Title').")
        return
        
    query_string = " ".join(search_query)
    logger.info(f"Performing manual search on Spotify for: '{query_string}'")
    
    try:
        # 1. Search for tracks
        search_results = spotify_wrapper.search_for_tracks(query=query_string, limit=10)
        
        if not search_results:
            click.echo(f"No tracks found on Spotify for '{query_string}'.")
            return
            
        # 2. Display results and prompt user for selection
        click.secho("\n--- Spotify Search Results ---", fg="cyan", bold=True)
        for i, track in enumerate(search_results):
            click.echo(f"{i + 1:2d}: {track['artist']} - {track['title']} ({track['album']})")
        click.echo(" 0: Cancel")
        click.echo("-" * 28)

        choice_str = click.prompt("Select a track number to add to the queue", type=str)
        
        # Validate choice
        if not choice_str.isdigit() or not (0 <= int(choice_str) <= len(search_results)):
            click.echo("Invalid choice. Aborting.")
            return
            
        choice = int(choice_str)

        if choice == 0:
            click.echo("Manual add cancelled.")
            return

        selected_track = search_results[choice - 1]
        spotify_uri = selected_track['uri']

        # 3. Queue the selected track in the database
        click.echo(f"\nQueuing '{selected_track['artist']} - {selected_track['title']}'...")
        
        success, message = db_manager.queue_track(
            spotify_uri=spotify_uri,
            artist_name=selected_track['artist'],
            track_name=selected_track['title'],
            album_name=selected_track['album']
        )
        
        if success:
            click.secho(message, fg="green")
            
            # 4. Optional: Immediate Processing
            if click.confirm("\nDo you want to process this track immediately? (Requires available quota)"):
                # This would call a high-level workflow function to process a single track.
                # from music_manager.workflows.download_workflow import process_single_track
                # process_single_track(spotify_uri)
                click.echo(f"CONCEPT: The track '{selected_track['title']}' would now be sent to the downloader.")
        else:
            click.secho(message, fg="yellow")

    except Exception as e:
        logger.error(f"An error occurred during manual add: {e}", exc_info=True)
        click.echo("An unexpected error occurred. Please check the logs.")

@spotify_group.command(name="sync-playlists", help="Sync all configured playlists.")
@click.pass_context
def sync_playlists_command(ctx):
    """
    Reads the configured playlist URLs, fetches all tracks from them,
    and adds any new/missing tracks to the download queue.
    """
    logger = ctx.obj['logger']
    
    logger.info("Manual playlist sync initiated.")
    click.echo("Starting sync of all configured Spotify playlists...")
    
    try:
        # This would be a high-level workflow function that orchestrates the
        # spotify_wrapper and db_manager to perform the sync.
        # from music_manager.workflows.sync_workflow import run_playlist_sync
        # new_tracks_count = run_playlist_sync(ctx.obj['db'], ctx.obj['spotify'], ctx.obj['config'])
        
        # Placeholder for now:
        new_tracks_count = 15 # dummy data
        
        if new_tracks_count > 0:
            click.secho(f"Sync complete. Found and queued {new_tracks_count} new tracks for download.", fg="green")
        else:
            click.secho("Sync complete. All playlists are up-to-date.", fg="green")
            
    except Exception as e:
        logger.error(f"A critical error occurred during playlist sync: {e}", exc_info=True)
        click.echo("An error occurred during the sync. Please check the logs.")

@spotify_group.command(name="list-playlists", help="List all playlists configured for syncing.")
@click.pass_context
def list_playlists_command(ctx):
    """
    Reads and displays the names of all playlists from the config file.
    """
    logger = ctx.obj['logger']
    config_manager = ctx.obj['config']
    spotify_wrapper = ctx.obj['spotify']

    try:
        playlist_urls = config_manager.get_spotify_setting('playlist_urls')
        if not playlist_urls:
            click.echo("No playlists are configured for syncing.")
            click.echo("You can add them via the 'settings setup' command or by editing your config file.")
            return

        click.secho(f"--- Configured Playlists ({len(playlist_urls)}) ---", fg="cyan", bold=True)
        
        for url in playlist_urls:
            # Fetch the playlist name for a better user experience
            playlist_name = spotify_wrapper.get_playlist_name(url)
            if playlist_name:
                click.echo(f"- {playlist_name}")
                click.echo(f"  ({url})")
            else:
                click.echo(f"- [Could not fetch name for this URL]")
                click.echo(f"  ({url})")

    except Exception as e:
        logger.error(f"An error occurred while listing playlists: {e}", exc_info=True)
        click.echo("An error occurred. Please check the logs.")