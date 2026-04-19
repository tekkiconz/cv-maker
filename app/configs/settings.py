from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    storage_path: str
    output_path: str
    templates_path: str

    model_config = {"env_file": ".env"}


settings = Settings()  # type: ignore[call-arg]
