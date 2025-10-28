# src/music_manager/api/routers/settings.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from music_manager.core.config_manager import ConfigManager
from music_manager.api.dependencies import get_config, get_app_context
from music_manager.api.models import ValidationResult
from music_manager.services.validation_service import ValidationService

router = APIRouter(
    prefix="/settings",
    tags=["Settings"],
)

class SettingsUpdate(BaseModel):
    section: str
    key: str
    value: Any

@router.get("/", summary="Get all configuration settings")
def get_settings(
    show_secrets: bool = False,
    config_manager: ConfigManager = Depends(get_config)
) -> Dict[str, Any]:
    """
    Retrieves the current application configuration.
    Sensitive values are masked by default.
    """
    config_dict = config_manager.get_config_as_dict() # type: ignore
    if show_secrets:
        return config_dict

    secrets_to_mask = ['client_secret', 'token', 'api_key', 'webhook_url']
    masked_config = {}
    for section, settings in config_dict.items():
        masked_config[section] = {}
        for key, value in settings.items():
            if key in secrets_to_mask:
                masked_config[section][key] = '********'
            else:
                masked_config[section][key] = value
    return masked_config

@router.post("/update", summary="Update a configuration setting")
def update_setting(
    update: SettingsUpdate,
    config_manager: ConfigManager = Depends(get_config)
):
    """
    Updates a specific setting in the configuration and saves the file.
    """
    try:
        config_manager.update_setting(update.section, update.key, update.value)
        config_manager.save_config()
        return {"message": f"Setting '{update.key}' in section '{update.section}' updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update setting: {e}")

@router.post("/validate", summary="Validate all external API connections", response_model=List[ValidationResult])
def validate_connections_api(app_context: dict = Depends(get_app_context)):
    """
    Performs a health check on all configured external services (Spotify, Plex, Lidarr)
    and core path configurations.
    """
    validation_service = ValidationService(app_context)
    results = validation_service.run_all_checks()

    # Convert the list of tuples to a list of Pydantic models for the response
    response_data = [ValidationResult(check_name=name, success=status, message=msg) for name, status, msg in results]
    return response_data