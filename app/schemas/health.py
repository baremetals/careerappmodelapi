from pydantic import BaseModel


class Health(BaseModel):
    name: str
    api_version: str
    app_model_version: str
