import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Build an absolute path to the .env file in the project root,
# regardless of which folder this script is actually run from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

print("Looking for .env at:", ENV_PATH)
print("File exists:", os.path.exists(ENV_PATH))


class Settings(BaseSettings):
    api_key: str
    database_url: str

    model_config = SettingsConfigDict(env_file=ENV_PATH)


settings = Settings()

if __name__ == "__main__":
    print("API key loaded:", settings.api_key)
    print("Database URL:", settings.database_url)