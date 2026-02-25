from pydantic_settings import BaseSettings, SettingsConfigDict

# Production db config
class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_name_test : str # used for the test db
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    alpha_vantage_api_key: str

    model_config = SettingsConfigDict(env_file = ".env")

settings = Settings()

