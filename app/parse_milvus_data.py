from typing import List, Union, Dict, Any
from app.schemas.embedding import MilvusHit


def process_search_results(results: List[Union[str, Dict[str, Any]]], user_interests: List[str] = None) -> (
        List)[Union[MilvusHit, Dict[str, Any]]]:
    # print(f"THE FUCKING INTERESTS================>: {user_interests}")
    if user_interests is None or len(user_interests) < 1:
        # Process as second set of results (structured format)
        return results
    else:
        # Process as first set of results (string format)
        return parse_milvus_hits(results[0])


def parse_milvus_hits(hits_obj) -> list:
    parsed_results = []

    for hit in hits_obj:
        hit_dict = {
            'id': hit.id,
            'distance': hit.distance,
            'entity': {}
        }
        parsed_results.append(hit_dict)

    return parsed_results
