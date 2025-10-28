# Use a specific Debian version for stability. 'bookworm' is a good modern choice.
FROM debian:bookworm-slim

# Set environment variables to prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Set up the working directory inside the container
WORKDIR /app

# Install dependencies
# - Add software-properties-common and gnupg to manage PPAs
# - Add the MusicBrainz PPA for Picard
# - Correct libchromaprint-tools to chromaprint-tools
# - Install all dependencies in a single RUN command to optimize layer caching
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    software-properties-common \
    gnupg \
    curl && \
    curl -fsSL https://ppa.launchpadcontent.net/musicbrainz-developers/stable/ubuntu/dists/jammy/Release.key | gpg --dearmor -o /etc/apt/trusted.gpg.d/musicbrainz.gpg && \
    add-apt-repository ppa:musicbrainz-developers/stable && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3-pip \
    build-essential \
    git \
    chromaprint-tools \
    picard \
    ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command to run when the container starts
CMD ["python", "src/music_manager/main.py", "watch"]