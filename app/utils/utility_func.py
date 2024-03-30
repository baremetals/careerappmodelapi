from slowapi import Limiter
from slowapi.util import get_remote_address
import time
import secrets

limiter = Limiter(key_func=get_remote_address)


def calculate_response_time(start_time: float) -> int:
    """
    Calculate the response time based on the start time of the request.
    The response time is returned in milliseconds.
    """
    end_time = time.time()
    response_time_ms = int((end_time - start_time) * 1000)  # Convert to milliseconds
    return response_time_ms


def unique_string(byte: int = 8) -> str:
    return secrets.token_urlsafe(byte)
