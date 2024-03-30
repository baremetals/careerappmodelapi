from pydantic import BaseModel


class LogData(BaseModel):
    api_key_id: int
    endpoint: str
    status: int
    method: str
    client_ip: str
    user_agent: str
    request_body: str
    error_message: str
    response_time: int  # in milliseconds
