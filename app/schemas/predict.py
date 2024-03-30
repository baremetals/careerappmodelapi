from typing import Any, List, Optional, Dict

from pydantic import BaseModel
from career_app_model.processing.validations import SingleResponseDataInputSchema


class PredictionResults(BaseModel):
    errors: Optional[Any]
    version: str
    selected_industries_scores: Optional[List[Dict]]
    # suitability_scores: Optional[List[List[float]]]
    suitability_scores: Optional[List[Dict]]
    # suitability_scores: Optional[List[Dict[str, Union[str, float]]]]


class PredictionInputs(BaseModel):
    inputs: List[SingleResponseDataInputSchema]
