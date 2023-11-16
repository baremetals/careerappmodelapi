from typing import Any, List, Optional

import numpy as np
from pydantic import BaseModel
from career_app_model.processing.validations import SingleResponseDataInputSchema


class PredictionResults(BaseModel):
    errors: Optional[Any]
    version: str
    predictions: Optional[List[float]]


class PredictionInputs(BaseModel):
    inputs: List[SingleResponseDataInputSchema]
