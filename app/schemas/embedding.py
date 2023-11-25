# from typing import Any, List, Optional
from pydantic import BaseModel


class EmbeddingsRequest(BaseModel):
    profileId: str
    interests: list
