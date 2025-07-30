from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB_NAME: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    FACE_API_KEY: str
    FACE_API_SECRET: str
    MAILJET_API_KEY: str
    MAILJET_API_SECRET: str
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    BASE_URL: str
    FACE_MATCH_THRESHOLD: int = 80

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8"
    )

settings = Settings()
