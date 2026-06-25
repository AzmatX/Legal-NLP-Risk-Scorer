from pydantic import BaseModel


class AppSettings(BaseModel):
    app_name: str = "AI Contract Intelligence API"
    app_version: str = "0.1.0"


settings = AppSettings()
