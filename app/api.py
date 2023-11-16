import json
from typing import Any

import numpy as np
import pandas as pd
from career_app_model.recommendation import recommend_roles
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from loguru import logger
from career_app_model import __version__ as app_model_version
from career_app_model.processing.validations import SingleResponseDataInputSchema
from career_app_model.predict import predict_suitability_scores

from app import __version__, schemas
from app.config import settings


api_router = APIRouter()


@api_router.get("/health", response_model=schemas.Health, status_code=200)
def health() -> dict:
    """
    Root Get
    """
    healthy = schemas.Health(
        name=settings.PROJECT_NAME, api_version=__version__, app_model_version=app_model_version
    )

    return healthy.model_dump()


@api_router.post("/predict", response_model=schemas.PredictionResults, status_code=200)
async def predict(input_data: schemas.PredictionInputs) -> Any:
    """
    Get user suitability scores for the all industries.
    """
    get_input_data = input_data.get('inputs')
    print(get_input_data)
    # Advanced: You can improve performance of your API by rewriting the
    # `make prediction` function to be async and using await here.
    logger.info(f"Making prediction on inputs: {input_data.inputs}")
    results = predict_suitability_scores(input_data=get_input_data)

    if results["errors"] is not None:
        logger.warning(f"Prediction validation error: {results.get('errors')}")
        raise HTTPException(status_code=400, detail=json.loads(results["errors"]))

    logger.info(f"Prediction results: {results.get('predictions')}")

    return results


@api_router.post("/embeddings/")
def get_job_roles(data: schemas.EmbeddingsRequest):
    # Retrieve embeddings from the Milvus database based on user interests
    # This is where you'll use your existing function to fetch the embeddings and get the closest matching job roles
    job_roles = recommend_roles(industry_data=data.interests)
    return {"job_roles": job_roles}


# @app.post("/predict/")
# def predict_suitability(data: PredictRequest, api_key: str = Depends(get_api_key)):
#     ...


# @app.post("/combined/")
# def combined_endpoint(data: PredictRequest):
#     # Predict suitability
#     results = predict_suitability_score(input_data=data.dict())
#
#     # Retrieve job roles based on interests (if provided)
#     if data.get("interests"):
#         job_roles = fetch_job_roles_from_embeddings(interests=data.interests)
#         results["job_roles"] = job_roles
#     return results
