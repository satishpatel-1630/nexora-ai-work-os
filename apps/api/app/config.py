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
    gemini_api_key:str|None=Field(None,alias="GEMINI_API_KEY"); gemini_model:str=Field("gemini-3.8-flash",alias="GEMINI_MODEL")
    ai_default_provider:str=Field("mock",alias="AI_DEFAULT_PROVIDER"); ai_max_cost:float=Field(1.0,alias="AI_MAX_COST"); ai_max_retries:int=Field(2,alias="AI_MAX_RETRIES"); ai_request_timeout:float=Field(60.0,alias="AI_REQUEST_TIMEOUT"); ai_research_enabled:bool=Field(True,alias="AI_RESEARCH_ENABLED")
    @property
    def cors_origins(self)->list[str]: return [x.strip() for x in self.cors_allowed_origins.split(",") if x.strip()]
@lru_cache
def get_settings()->Settings: return Settings()
