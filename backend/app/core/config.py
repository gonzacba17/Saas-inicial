from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    project_name: str = "SaaS Inicial"
    version: str = "1.0.0"
    api_v1_str: str = "/api/v1"
    
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    database_url: str
    
    openai_api_key: Optional[str] = None
    mercadopago_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()