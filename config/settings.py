import os
from pathlib import Path
from dotenv import load_dotenv
from core.exceptions import ConfigurationError

# Resolve base directory path
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment variables from root .env
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    """
    Centralized settings loader and validator for the FinSight application.
    Parses environment variables and checks constraints.
    """

    def __init__(self):
        self.PROJECT_NAME: str = "FinSight"
        self.BASE_DIR: Path = BASE_DIR
        
        # Load environment values
        self.APP_ENV: str = os.getenv("APP_ENV", "development").lower()
        if self.APP_ENV not in ["development", "production", "testing"]:
            raise ConfigurationError(
                f"Invalid APP_ENV: '{self.APP_ENV}'. Must be one of: development, production, testing."
            )

        # Parse debug mode: defaults to True in development/testing, False in production
        debug_str = os.getenv("DEBUG")
        if debug_str is not None:
            clean_debug = debug_str.lower()
            if clean_debug in ["true", "1", "t", "yes", "y"]:
                self.DEBUG: bool = True
            else:
                self.DEBUG: bool = False
        else:
            if self.APP_ENV == "production":
                self.DEBUG: bool = False
            else:
                self.DEBUG: bool = True

        # Log level validation
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.LOG_LEVEL not in valid_log_levels:
            raise ConfigurationError(
                f"Invalid LOG_LEVEL: '{self.LOG_LEVEL}'. Must be one of: {', '.join(valid_log_levels)}"
            )

        # File paths
        self.LOG_DIR: Path = self.BASE_DIR / "logs"
        self.LOG_FILE_PATH: Path = self.LOG_DIR / "finsight.log"
        self.DATA_DIR: Path = self.BASE_DIR / "data"

        # API settings
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        self.GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV == "testing"


# Singleton instance of application settings
settings = Settings()
