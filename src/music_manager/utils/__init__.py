# src/music_manager/utils/__init__.py

"""
MusicManager Utilities Package
------------------------------

This package contains miscellaneous helper functions and utility classes that are
used across different parts of the MusicManager application.

These utilities are designed to be generic and self-contained, handling common
tasks that are not specific to any single service or component.

Modules:
- processes: Contains helper functions for running and managing external
  command-line processes, such as 'onthespot' and 'picard'.
"""

# The __all__ variable defines the public API of this package. It makes it
# clear which functions or classes are intended for general consumption by
# other modules within the application.
__all__ = [
    "run_external_process",
]