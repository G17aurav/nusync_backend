from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_minutes: int = 60 * 24 * 7
    mfa_pending_token_expire_minutes: int = 5

    mfa_issuer: str = "NuSync"

    class Config:
        env_file = ".env"


settings = Settings()
