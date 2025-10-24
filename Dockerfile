# Dockerfile

# Use the linuxserver.io base image, which is based on Ubuntu 22.04 (jammy).
# This image has comprehensive repositories and a robust permission model.
FROM lsiobase/ubuntu:jammy

# Set environment variables for Python using the modern key=value format
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --- Install System & Python Dependencies ---
# This single RUN command updates repositories, installs all system dependencies,
# and then cleans up to keep the image size down.
RUN \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    # --- Python and its core tools ---
    python3.11 \
    python3.11-venv \
    python3-pip \
    # --- Git is required by some release tools and is good practice ---
    git \
    # --- Critical Application Runtime Dependencies ---
    libchromaprint-tools \
    picard \
    ffmpeg && \
    # --- Cleanup ---
    rm -rf /var/lib/apt/lists/*

# Set the application's working directory
WORKDIR /app

# Copy dependency files first to leverage Docker's layer caching
COPY requirements.txt pyproject.toml ./

# Install Python packages into a dedicated virtual environment
RUN \
    python3.11 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the application's source code
COPY src/ /app/src

# --- Final Configuration ---
# The lsiobase image uses PUID/PGID to manage permissions on startup.
# We ensure the application directories are owned by the 'abc' user
# that the lsiobase image provides.
RUN chown -R abc:abc /app /opt/venv

# Add the virtual environment's bin directory to the system's PATH
ENV PATH="/opt/venv/bin:$PATH"

# Define the default command to run when the container starts.
# This starts the application in 'watch' mode, the intended behavior for a service.
CMD ["python3.11", "src/music_manager/main.py", "watch"]