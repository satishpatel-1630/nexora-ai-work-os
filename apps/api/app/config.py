from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env",env_file_encoding="utf-8",extra="ignore")
    app_name:str="NEXORA API"; version:str="0.1.0"
    environment:str=Field("development",alias="NEXORA_ENV"); api_host:str=Field("0.0.0.0",alias="NEXORA_API_HOST"); api_port:int=Field(8000,alias="NEXORA_API_PORT")
    database_url:str=Field("postgresql+asyncpg://nexora:nexora@localhost:5432/nexora",alias="DATABASE_URL")
    redis_url:str=Field("redis://localhost:6379/0",alias="REDIS_URL")
    cors_allowed_origins:str=Field("http://localhost:3000",alias="CORS_ALLOWED_ORIGINS"); log_level:str=Field("INFO",alias="LOG_LEVEL")
    openai_api_key:str|None=Field(None,alias="OPENAI_API_KEY"); google_api_key:str|None=Field(None,alias="GOOGLE_API_KEY"); anthropic_api_key:str|None=Field(None,alias="ANTHROPIC_API_KEY")
    github_token:str|None=Field(None,alias="GITHUB_TOKEN"); vercel_token:str|None=Field(None,alias="VERCEL_TOKEN")
    @property
    def cors_origins(self)->list[str]: return [x.strip() for x in self.cors_allowed_origins.split(",") if x.strip()]
@lru_cache
def get_settings()->Settings: return Settings()
