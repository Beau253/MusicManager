# src/music_manager/api/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager

from music_manager.api.dependencies import initialize_dependencies, db_manager
from music_manager.api.routers import settings, db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on application startup
    print("--- Starting MusicManager API ---")
    initialize_dependencies()
    print("--- Dependencies initialized ---")
    yield
    # Code to run on application shutdown
    if db_manager:
        db_manager.close()
    print("--- MusicManager API Shutting Down ---")


app = FastAPI(
    title="MusicManager API",
    description="A RESTful API to control the MusicManager application.",
    version="1.0.0",
    lifespan=lifespan
)

# Include the routers from the different modules
app.include_router(settings.router)
app.include_router(db.router)
# Future routers for plex, lidarr, etc. would be included here

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the MusicManager API"}