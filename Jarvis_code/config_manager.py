import json
import os
import logging
from typing import Dict, Any, Optional

# Constants
CONFIG_FILE_NAME = "user_config.json"
# Config file is located one level up from this file (in root of Jarvis)
CONFIG_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", CONFIG_FILE_NAME))

logger = logging.getLogger("config_manager")

class ConfigManager:
    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self) -> None:
        """Loads configuration from user_config.json"""
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.info(f"Loaded configuration from {CONFIG_FILE_PATH}")
            except Exception as e:
                logger.error(f"Failed to load user_config.json: {e}")
                self._config = {}
        else:
            logger.warning(f"Configuration file not found at {CONFIG_FILE_PATH}. Using defaults or waiting for setup.")
            self._config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a value from the config using dot notation for nested keys.
        Example: config.get("llm.provider", "google")
        """
        keys = key.split('.')
        value = self._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def save_config(self) -> None:
        """Saves current configuration to file"""
        try:
            with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4)
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def ensure_user_id(self) -> str:
        """
        Ensures a stable user_id exists in config. 
        If missing, generates it from user_name or default, and saves key.
        This provides the separation between persistent ID and display name.
        """
        if "user_id" not in self._config:
            # Fallback: Use current user_name as base for ID, or generate one
            # Using user_name ensures backward compat (memories attached to "Siddh" stay with "Siddh")
            current_name = self.get("user_name", "primary_user")
            # Sanitize to be a clean ID (optional, but keeping it same as name for backward compat is safer for Mem0)
            self._config["user_id"] = current_name
            self.save_config()
            logger.info(f"Generated and saved new persistent user_id: {current_name}")
        
        return self._config["user_id"]

    def get_api_key(self, service: str) -> Optional[str]:
        """Helper to get API keys easily"""
        return self.get(f"api_keys.{service}")

    def get_user_id(self) -> str:
        """
        INTERNAL IDENTITY: Returns the persistent user_id for memory operations.
        Never changes even if user changes their display name.
        """
        return self.ensure_user_id()

    def get_user_name(self) -> str:
        """
        DISPLAY NAME: Returns the user's spoken/display name.
        This is editable by the user.
        """
        # Alias for get_full_name preference, keeping method name for compatibility or updating
        return self.get("user_name", "User")

    def get_full_name(self) -> str:
        """Explicit alias for display name"""
        return self.get_user_name()
        
    def get_assistant_name(self) -> str:
        """Helper to get assistant name"""
        return self.get("assistant_name", "Jarvis")
    
    def get_llm_config(self) -> Dict[str, str]:
        """Helper to get LLM config"""
        return self.get("llm", {"provider": "google", "model": "gemini-2.5-flash-native-audio-preview-09-2025"})

    def get_mem0_key(self) -> Optional[str]:
        """Helper to get Mem0 API key"""
        return self.get_api_key("mem0")

    def get_google_search_key(self) -> Optional[str]:
        """Helper to get Google Search API key"""
        return self.get_api_key("google_search")
    
    def get_search_engine_id(self) -> Optional[str]:
        """Helper to get Search Engine ID"""
        return self.get_api_key("search_engine_id")
    
    def get_openweather_key(self) -> Optional[str]:
        """Helper to get OpenWeather API key"""
        return self.get_api_key("openweather")
