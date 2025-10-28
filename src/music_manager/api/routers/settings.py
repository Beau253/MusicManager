# src/music_manager/api/routers/settings.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from music_manager.core.config_manager import ConfigManager
from music_manager.api.dependencies import get_config

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