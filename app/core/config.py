from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = ""
    PROJECT_VERSION: str = ""
    PROJECT_DESCRIPTION: str = ""
    API_VERSION: str = ""
    DEBUG: bool = True

    # CORS Origin Configuration
    CORS_ORIGINS: list[str] = []

    # ElasticSearch related settings
    ES_URL: str = ""
    ES_STACK_VERSION: str = ""
    ES_STACK_PORT: str = ""

    # Development Settings
    HOST: str = ""
    PORT: str = ""

    # Logger Configuration
    PRODUCTION_LOG_FILE: str = ""

    # Dataset File
    DATASET_FILE: str = ""

    class Config:
        env_file = ".env"
        env_prefix = "FASTAPI_ES_"
        case_sensitive = True


settings = Settings()
