from typing import Any, List, Optional

from pydantic import BaseModel
from career_app_model.processing.validations import SingleResponseDataInputSchema


class PredictionResults(BaseModel):
    errors: Optional[Any]
    version: str
    suitability_scores: Optional[List[List[float]]]


class PredictionInputs(BaseModel):
    inputs: List[SingleResponseDataInputSchema]
