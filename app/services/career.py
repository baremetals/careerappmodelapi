import time
import json

from career_app_model.recommendation import recommend_roles
from fastapi import HTTPException
from loguru import logger

from app.get_suitability_scores import get_suitability_scores
from app.parse_milvus_data import process_search_results
from app.schemas import LogData
from app.services.log_data import create_api_log
from app.utils.utility_func import calculate_response_time


async def get_industry_predictions(data, request, api_key):
    start_time = time.time()
    response_status: int = 200
    error_message = ''
    try:
        input_data = {
            "profileId": data.profileId,
            "selectedIndustries": data.selectedIndustries,
            "selectedInterests": data.selectedInterests,
            "responses": data.responses
        }
        results = get_suitability_scores(input_data=input_data)
        if results["errors"] is not None:
            raise HTTPException(status_code=400, detail=json.loads(results["errors"]))
        return results
    except Exception as e:
        response_status = 500
        error_message = str(e)
        logger.exception(e)
        raise HTTPException(status_code=response_status, detail=error_message)
    finally:
        client_host = request.client.host
        x_forwarded_for = request.headers.get('X-Forwarded-For')
        real_ip = x_forwarded_for or client_host
        response_time = calculate_response_time(start_time)
        log_data = LogData(
            api_key_id=api_key.id,
            endpoint="/predict",
            status=response_status,
            client_ip_address=real_ip,
            user_agent=request.headers.get('User-Agent'),
            request_body=json.dumps(data),
            error_message=error_message,
            response_time=response_time
        )

        await create_api_log(log_data)


async def fetch_predicted_job_roles(data, request, api_key):
    start_time = time.time()
    response_status: int = 200
    error_message = ''

    try:
        user_interests = data.user_interests
        if user_interests is None or len(user_interests) < 1:
            user_interests = None
        search_results = recommend_roles(industry_data=data.chosen_industries, user_interests=user_interests)
        job_roles = process_search_results(results=search_results, user_interests=user_interests)
        return {"job_roles": job_roles}
    except Exception as e:
        response_status = 500
        error_message = str(e)
        raise HTTPException(status_code=response_status, detail=error_message)
    finally:
        client_host = request.client.host
        x_forwarded_for = request.headers.get('X-Forwarded-For')
        real_ip = x_forwarded_for or client_host
        response_time = calculate_response_time(start_time)
        log_data = LogData(
            api_key_id=api_key.id,
            endpoint="/embeddings",
            status=response_status,
            client_ip_address=real_ip,
            user_agent=request.headers.get('User-Agent'),
            request_body=json.dumps(data),
            error_message=error_message,
            response_time=response_time
        )
        await create_api_log(log_data)
