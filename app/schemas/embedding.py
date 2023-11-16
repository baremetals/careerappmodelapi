# from typing import Any, List, Optional
from pydantic import BaseModel


class EmbeddingsRequest(BaseModel):
    userId: str
    interests: list
