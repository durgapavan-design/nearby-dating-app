from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://dating:dating@db:5432/dating"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days, MVP: no refresh token flow
    otp_expire_minutes: int = 5
    otp_debug_mode: bool = True  # returns the OTP code in the API response instead of sending SMS
    upload_dir: str = "uploads"
    max_photos_per_user: int = 6


settings = Settings()
