# src/music_manager/services/__init__.py

"""
MusicManager Services Package
-----------------------------

This package contains higher-level modules that orchestrate the core components
and external wrappers to perform specific business logic and workflows.

These services are the "glue" that connects the user's intent (from the CLI)
to the actions performed by the application.

Modules:
- downloader: Contains the logic for the track acquisition workflow, managing
  the download queue, calling 'onthespot', and handling retries/fallbacks.
- organizer: Contains the logic for the metadata processing workflow, calling
  MusicBrainz Picard, reading new tags, and populating the database.
- playlist_generator: Handles the creation and updating of .m3u playlist files
  based on the contents of the database.
"""

# The __all__ variable defines the public API of this package, making it
# clear which classes or functions are intended for use by other parts of
# the application, such as the CLI command modules.
__all__ = [
    "DownloaderService",      # A conceptual class from downloader.py
    "OrganizerService",       # A conceptual class from organizer.py
    "PlaylistGenerator",      # The class from playlist_generator.py
]