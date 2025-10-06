from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_PORT: int 
    REDIS_HOST: str 
    REDIS_PASSWORD: str 

    class Config:
        env_file = ".env"

settings = Settings()
