from fastapi import APIRouter, Request, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from app.config.guards import get_current_user, verify_api_key
from app.models.user import APIKey
from app.config.database import get_db
from loguru import logger
from app import schemas
from app.services.career import get_industry_predictions, fetch_predicted_job_roles
from app.utils.utility_func import limiter

router = APIRouter()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/predict", response_model=schemas.PredictionResults, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def predict(request: Request, input_data: schemas.PredictionInputs,
                  api_key: APIKey = Depends(verify_api_key)) -> dict:
    """
    Get user suitability scores for the all industries.
    """
    logger.info('predicting starting------------------<')
    get_input_data = input_data.inputs[0]
    return await get_industry_predictions(get_input_data, request, api_key)


@router.post("/embeddings/", response_model=schemas.EmbeddingsResults, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_job_roles(request: Request, data: schemas.EmbeddingsRequest,
                        api_key: APIKey = Depends(verify_api_key)):
    # logger.info(f"FETCHING EMBEDDINGS mate------------------<")
    return await fetch_predicted_job_roles(data, request, api_key)
