import logging
from typing import List, Dict, Any, Tuple, Optional

# Import the third-party library
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
                    )
                    self.sp = spotipy.Spotify(auth_manager=auth_manager)
                    logger.debug("Spotify client initialized successfully.")
                except SpotifyException as e:
                    # Catch specific spotipy exceptions during initialization
                    logger.error(f"Failed to initialize Spotify client due to authentication error: {e}", exc_info=True)
                    self.sp = None
                except Exception as e: # Catch any other unexpected errors
                    logger.error(f"Failed to initialize Spotify client: {e}", exc_info=True)
                    self.sp = None
    
        def is_configured(self) -> bool:
            """Checks if the necessary Spotify credentials are provided."""
            return bool(self.client_id and self.client_secret)

        def _check_client(self):
            """Raises an exception if the client is not configured or initialized."""
            if not self.sp:
                raise ConnectionError("Spotify client is not configured or failed to initialize. Please check credentials.")

        def validate_connection(self) -> tuple[bool, str]:
            """
            """
            if not self.is_configured():
                return False, "Spotify is not configured."
            self._check_client()

            logger.debug("Validating Spotify connection by fetching user profile...")
            try:
            logger.error(error_message)
            return False, error_message

    def get_playlist_tracks(
        self, playlist_id_or_url: str, fields: str = 'full'
    ) -> Tuple[Optional[str], List[Any]]:
        """
        Fetches all tracks from a given Spotify playlist URL or ID.

        This method handles pagination to retrieve all tracks from the playlist.
        It also returns the playlist's name.

        Args:
            playlist_id_or_url: The URL or ID of the Spotify playlist.
            fields: The level of detail to return for each track.
                    'full' (default): Returns a list of full track dictionaries.
                    'uri': Returns a list of Spotify URI strings.
        
        Returns:
            A tuple containing the playlist name (str) and a list of track
            items (dictionaries or strings). Returns (None, []) if the
            playlist is not found or an error occurs.
        """
        self._check_client()
        try:
            logger.info(f"Fetching playlist details and tracks for: {playlist_id_or_url}")
            
            # Define the fields to request from the API based on the desired output
            api_fields = "name,tracks.items.track(uri,name,artists(name),album(name)),tracks.next"
            if fields == 'uri':
                api_fields = "name,tracks.items.track.uri,tracks.next"

            playlist_data = self.sp.playlist(playlist_id_or_url, fields=api_fields)

            if not playlist_data:
            
                logger.warning(f"Could not find playlist '{playlist_id_or_url}' or it is empty.")
                return None, []

            playlist_name = playlist_data.get('name', 'Unknown Playlist')
            results = playlist_data.get('tracks')

            tracks = []
            while results:
                if fields == 'uri':
                            tracks.append(track_data.get('uri'))
                        else: # 'full'
                            tracks.append({
                                'uri': track_data.get('uri'),
                                'artist': ', '.join([artist['name'] for artist in track_data.get('artists', [])]),
                                'title': track_data.get('name'),
                                'album': track_data.get('album', {}).get('name')
                            })
                results = self.sp.next(results) if results['next'] else None

            return playlist_name, tracks

        except SpotifyException as e:
            logger.error(f"A Spotify API error occurred while fetching playlist tracks: {e.msg}")
            return None, []
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching playlist tracks: {e}", exc_info=True)
            return None, []

    def search_for_tracks(self, query: str, limit: int = 10) -> list[dict]:
            A list of track dictionaries, each containing 'uri', 'artist',
            'title', and 'album'.
        
        self._check_client()
        try:
            logger.info(f"Searching Spotify for query: '{query}' with limit {limit}")
            results = self.sp.search(q=query, type='track', limit=limit)
            logger.error(f"A Spotify API error occurred during search: {e.msg}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred during track search: {e}", exc_info=True)
            return []