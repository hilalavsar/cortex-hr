from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Cortex HR"
    lm_studio_url: str = "http://192.168.219.1:1234/v1"
    model_name: str = "phi3-mini-guvenli@q8_0"
    secret_key: str = "gelistirme-icin-gecici-anahtar-degistir"
    algorithm: str = "HS256"
    token_expire_minutes: int = 60

settings = Settings()