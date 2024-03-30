from typing import Any, List, Dict
# from app import schemas
from career_app_model.predict import predict_suitability_scores
from career_app_model.datasets import industry_names
from loguru import logger


def get_suitability_scores(input_data: dict) -> dict[str, list[dict] | None | Any]:
    suitability_scores = predict_suitability_scores(input_data=input_data)
    selected_industries = input_data.get("selectedIndustries", [])
    all_industries = industry_names.get_industry_names()
    predicted_scores = suitability_scores.get('suitability_scores')
    filtered_scores = {industry: score for industry, score in zip(all_industries, predicted_scores[0])}

    # Create an array of objects
    industry_scores: List[Dict] = [{"industryName": industry, "score": score} for industry, score in
                                   filtered_scores.items()]

    # Filter the industry_scores array
    filtered_industry_scores: List[Dict] = [item for item in industry_scores if item["industryName"] in
                                            selected_industries]

    version_tuple = suitability_scores.get("version", 'default_version')
    version = version_tuple[0] if version_tuple else 'default_version'
    errors = suitability_scores.get('errors')
    logger.info(f"====================================> the version: {version}")
    # print(f"the error: {errors}, the version: {version}")

    results = {
        "suitability_scores": industry_scores,
        "selected_industries_scores": filtered_industry_scores,
        "version": version,
        "errors": errors
    }

    return results
