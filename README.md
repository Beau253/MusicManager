# MusicManager

<div align="center">

**A powerful, automated management console for your local music library.**

*MusicManager is an intelligent, self-hosted application that acts as the central brain for your music collection. It automatically syncs with Spotify, downloads new tracks, enriches metadata using MusicBrainz, and integrates deeply with your existing media servers like Lidarr and Plex.*

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE.md)
[![Discord](https://img.shields.io/discord/YOUR_DISCORD_SERVER_ID?label=Community&logo=discord&style=for-the-badge)](https://discord.gg/YOUR_INVITE_CODE)

</div>

---

## Key Features

*   **Automated Spotify Sync**: "Watch" your favorite Spotify playlists and automatically download any new tracks you add.
*   **MusicBrainz-First Metadata**: All metadata is sourced from MusicBrainz for unparalleled accuracy and consistency, using AcoustID fingerprinting to identify tracks.
*   **Full Lidarr Integration**:
    *   Avoids duplicate downloads by checking if Lidarr already has or is grabbing an album.
    *   Triggers targeted post-download scans in Lidarr for seamless importing.
    *   Manage Lidarr directly from the CLI: view the queue, add artists, refresh, and more.
*   **Deep Plex Integration**:
    *   Create and sync native Plex playlists.
    *   Verify that your local files have been correctly scanned into your Plex library.
    *   Trigger library scans and other commands directly from the CLI.
*   **Robust & Resilient**: A persistent SQLite database tracks the lifecycle of every song, preventing re-downloads and gracefully handling failures.
*   **Powerful CLI Console**: A hierarchical, menu-driven Command-Line Interface provides full control over every aspect of your library and its integrations.
*   **Library Scanner**: Onboard your existing music library by scanning local files, identifying them with MusicBrainz, and populating the database.
*   **Secrets Management**: Securely manage your API keys using a `.env` file for local development and environment variables for production.
*   **Docker-Ready**: Designed from the ground up to be run in a Docker container for a clean, portable, and isolated setup.

## Installation

The recommended and most straightforward method for running MusicManager is using Docker and Docker Compose.

### Docker Installation (Recommended)

1.  **Prerequisites:**
    *   `Docker` and `Docker Compose` installed on your system.
    *   `git` for cloning the repository.

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/MusicManager.git
    cd MusicManager
    ```

3.  **Prepare Host Directories:**
    Create the necessary directories on your host machine that will be mounted into the container.
    ```bash
    mkdir config music logs
    ```

4.  **Configure Environment Variables:**
    Copy the example `.env` file and edit it to add your secret API keys and URLs.
    ```bash
    cp .env.example .env
    nano .env
    ```
    Fill in all `YOUR_...` placeholders with your actual credentials.

5.  **Configure `docker-compose.yml`:**
    *   **User Permissions:** Find your user and group ID on your host system by running `id`.
      ```bash
      id
      # Example output: uid=1000(myuser) gid=1000(myuser)
      ```
      Open `docker-compose.yml` and change the `PUID` and `PGID` values to match your `uid` and `gid`. This prevents file permission issues.
    *   **Music Library Path:** **This is the most important step.** Change the music volume mapping to point to your *actual* music library on your host machine.
      ```yaml
      volumes:
        # ... other volumes ...
        # Change the path on the LEFT side of the colon:
        - /path/to/your/actual/music/library:/music
      ```

6.  **Build and Run the Container:**
    ```bash
    docker-compose up --build -d
    ```
    The application will now be running in the background.

7.  **Run the Interactive Setup:**
    The first time you run the container, you should run the interactive setup wizard to create your initial `config.toml` file. This is also where you will define your music library path *as seen by the container* (which should be `/music` if you followed the steps above).
    ```bash
    docker-compose exec musicmanager python src/music_manager/main.py setup
    ```    Follow the prompts to configure all necessary paths and settings.

### Bare Metal Installation (Advanced)

This method is for users who do not wish to use Docker.

1.  **Prerequisites:**
    *   Python 3.9+
    *   `git`
    *   **MusicBrainz Picard**: Must be installed and accessible in your system's `PATH`.
    *   **`fpcalc`**: The AcoustID fingerprinting tool. On Debian/Ubuntu, install with `sudo apt-get install chromaprint-tools`.

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/MusicManager.git
    cd MusicManager
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure:**
    *   Copy `.env.example` to `.env` and fill in your secrets.
    *   Run the setup wizard: `python src/music_manager/main.py setup`.

5.  **Run the Application:**
    *   To run in the background (daemon mode):
      ```bash
      python src/music_manager/main.py watch
      ```
    *   To access the CLI menu:
      ```bash
      python src/music_manager/main.py
      # (This will be expanded to launch the full menu)
      ```

## Command-Line Usage

Once running, you can interact with the application using the CLI.

**Accessing the CLI (Docker):**
```bash
docker-compose exec musicmanager python src/music_manager/main.py <command>
```
*Example:* `docker-compose exec musicmanager python src/music_manager/main.py plex scan-library`

### Top-Level Commands

*   `watch`: Starts the application in daemon mode, running periodic syncs and health checks. (This is the default command for the Docker container).
*   `setup`: Runs the interactive configuration wizard.
*   `validate`: Performs a health check on your configuration, paths, dependencies, and all API connections.
*   `run-workflow`: Manually triggers a single, full daily workflow run.

### Service Menus

The CLI is organized into logical groups.

*   `spotify <command>`: Tools for interacting with Spotify (e.g., `manual-add`, `force-sync`).
*   `downloader <command>`: Manage the download queue (e.g., `view-queue`, `retry-failed`).
*   `library <command>`: Manage your local library (e.g., `scan-library`, `search`, `stats`).
*   `plex <command>`: A full suite of commands to interact with your Plex server (e.g., `scan-library`, `list-playlists`, `find-track`).
*   `lidarr <command>`: A full suite of commands to interact with your Lidarr instance (e.g., `view-queue`, `add-artist`, `refresh-artist`).
*   `db <command>`: Perform low-level management of the application's database (e.g., `list`, `info`, `remove`).
*   `settings <command>`: View and manage application settings.

## Support & Community

<div align="center">

**Having trouble or have a great idea? Join our Discord server!**

[![Discord](https://img.shields.io/discord/YOUR_DISCORD_SERVER_ID?label=Join%20the%20Community&logo=discord&style=for-the-badge&logoColor=white)](https://discord.gg/YOUR_INVITE_CODE)

</div>

The official Discord server is the best place to get help, ask questions, request new features, and share how you're using MusicManager.

You can also run the built-in support command to get the invite link at any time:
```bash
# Docker
docker-compose exec musicmanager python src/music_manager/main.py support

# Bare Metal
python src/music_manager/main.py support
```

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.