from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = Field(..., env="DATABASE_URL")

    # Redis
    redis_url: str = Field(..., env="REDIS_URL")

    # Google OAuth
    google_client_id: str = Field(..., env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    
    # JWT
    jwt_secret: str = Field(..., env="JWT_SECRET")

    # Groq
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    groq_model: str = Field(default="openai/gpt-oss-120b", env="GROQ_MODEL")
    groq_fast_model: str = Field(default="openai/gpt-oss-20b", env="GROQ_FAST_MODEL")

    # Tavily
    tavily_api_key: str = Field(default="", env="TAVILY_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
