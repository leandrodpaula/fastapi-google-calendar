import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class MongoSettings(BaseSettings):
    # Default values can be provided, and they can be overridden by environment variables
    # Example: export MONGO_URI="mongodb://user:pass@custom_host:27017/"
    # The variable names are case-insensitive for BaseSettings.

    MONGO_URI: str = "mongodb://localhost:27017/event_planner_db"
    MONGO_DATABASE_NAME: str = "event_planner_db" # Can be part of URI or separate

    # If your MONGO_URI includes the database name, MONGO_DATABASE_NAME might be redundant
    # or used to ensure the correct DB is targeted if the client connects to the root server.
    # For Motor, the database is typically accessed as client[database_name].

    # For local development, you might not have user/password.
    # For production, these should definitely be set via environment variables.
    # MONGO_USER: Optional[str] = None
    # MONGO_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env" # Specifies a file to load environment variables from (optional)
        env_file_encoding = 'utf-8'
        extra = 'ignore' # Ignore extra fields from .env file

@lru_cache() # Cache the settings object, so it's created only once
def get_mongo_settings() -> MongoSettings:
    """
    Returns the MongoDB settings instance.
    The settings are loaded from environment variables or a .env file.
    Caching ensures that the .env file is read and settings are parsed only once.
    """
    return MongoSettings()

# Example usage (not part of the module's direct execution, just for illustration):
# if __name__ == "__main__":
#     settings = get_mongo_settings()
#     print(f"Mongo URI: {settings.MONGO_URI}")
#     print(f"Mongo Database Name: {settings.MONGO_DATABASE_NAME}")
