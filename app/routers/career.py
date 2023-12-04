from fastapi import APIRouter, HTTPException
from typing import Any

from starlette import status

from app.get_suitability_scores import get_suitability_scores
from app.parse_milvus_data import process_search_results
from career_app_model.recommendation import recommend_roles
from loguru import logger
import json
from app import schemas
router = APIRouter()


@router.post("/predict", response_model=schemas.PredictionResults, status_code=status.HTTP_200_OK)
async def predict(input_data: schemas.PredictionInputs) -> Any:
    """
    Get user suitability scores for the all industries.
    """
    logger.info('predicting starting------------------<')
    get_input_data = input_data.inputs[0]
    new_input_data = {
        "profileId": get_input_data.profileId,
        "selectedIndustries": get_input_data.selectedIndustries,
        "selectedInterests": get_input_data.selectedInterests,
        "responses": get_input_data.responses
    }

    # logger.info(f"Making prediction on inputs: {industry_names.get_industry_names()}")
    results = get_suitability_scores(input_data=new_input_data)

    # logger.info(f"Filtering names: {filtered_predictions}")
    if results["errors"] is not None:
        # logger.warning(f"Prediction validation error: {results.get('errors')}")
        raise HTTPException(status_code=400, detail=json.loads(results["errors"]))

    # logger.info(f"Prediction results: {results.get('suitability_scores')}")
    return results


@router.post("/embeddings/", response_model=schemas.EmbeddingsResults, status_code=status.HTTP_200_OK)
def get_job_roles(data: schemas.EmbeddingsRequest):
    # logger.info(f"FETCHING EMBEDDINGS mate------------------<")
    user_interests = data.user_interests
    if user_interests is None or len(user_interests) < 1:
        user_interests = None
    search_results = recommend_roles(industry_data=data.chosen_industries, user_interests=user_interests)
    job_roles = process_search_results(results=search_results, user_interests=user_interests)
    # logger.info(f"JUST------------------<:{job_roles}")

    return {"job_roles": job_roles}
