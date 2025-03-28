from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    # Redis settings
    REDIS_ENABLED: bool = True
    REDIS_URL: str = "redis://localhost:6379"
    
    # Server settings
    PORT: int = 9500
    HOST: str = "0.0.0.0"
    
    # Cache TTL settings (in seconds)
    CACHE_TTL_CATEGORIES: int = 86400  # 1 day
    CACHE_TTL_EMOJIS: int = 14400      # 4 hours
    
    # API settings
    SLACKMOJIS_BASE_URL: str = "https://slackmojis.com"
    EMOJIS_API_URL: str = "https://api.emojis.com/api/graphql"
    
    class Config:
        env_prefix = ""
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 