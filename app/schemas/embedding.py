from typing import Dict, List, Union, Optional
from pydantic import BaseModel


class EmbeddingsRequest(BaseModel):
    chosen_industries: List[Dict[str, Union[str, float]]]
    user_interests: Optional[List[str]]


class MilvusHit(BaseModel):
    id: str
    distance: float
    entity: Dict


# class MilvusResults(BaseModel):
#     results: List[MilvusHit]


class MilvusHitDict(BaseModel):
    role_id: str
    industries: List[str]


class EmbeddingsResults(BaseModel):
    # job_roles: Union[MilvusHit, MilvusHitDict]
    job_roles: Union[List[MilvusHit], List[MilvusHitDict]]
