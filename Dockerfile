# Dockerfile

# -----------------------------------------------------------------------------
# Stage 1: Builder
# -----------------------------------------------------------------------------
# This stage installs dependencies and builds the application. Using a separate
# build stage keeps the final image smaller and cleaner.
# Using a specific version is a best practice for reproducible builds.
FROM python:3.11-slim as builder

# Set the working directory inside the container
WORKDIR /app

# Set environment variables to optimize Python in Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install essential system dependencies required for building Python packages
# and for the application's runtime dependencies (Picard, fpcalc).
# - git: Required by semantic-release plugins if needed.
# - build-essential: For compiling any C extensions in Python packages.
# - chromaprint-tools: Provides the 'fpcalc' command for AcoustID.
# - picard: The MusicBrainz Picard application itself.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    build-essential \
    chromaprint-tools \
    picard && \
    rm -rf /var/lib/apt/lists/*

# Copy the dependency files first to leverage Docker's layer caching.
# This layer will only be rebuilt if requirements.txt or pyproject.toml changes.
COPY requirements.txt pyproject.toml ./

# Install the Python dependencies into a virtual environment for isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container
COPY src/ /app/src/

# -----------------------------------------------------------------------------
# Stage 2: Final Production Image
# -----------------------------------------------------------------------------
# Start from a clean, slim base image for the final product.
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install only the necessary RUNTIME system dependencies, not build tools.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    chromaprint-tools \
    picard && \
    rm -rf /var/lib/apt/lists/*

# Copy the virtual environment with installed packages from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Copy the application source code from the builder stage.
COPY --from=builder /app/src /app/src

# Create a non-root user to run the application for enhanced security.
# The user's home directory will be /home/appuser.
RUN useradd --create-home --shell /bin/bash appuser

# Switch to the non-root user.
USER appuser

# Make the virtual environment's bin directory available in the PATH.
ENV PATH="/opt/venv/bin:$PATH"

# Define the default command to run when the container starts.
# This will start the application in 'watch' mode by default, which is
# the intended behavior for a long-running service.
CMD ["python", "src/music_manager/main.py", "watch"]