from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.log import APILog
from app.schemas import LogData

db_dependency = Annotated[Session, Depends(get_db)]
db: db_dependency


async def create_api_log(log_data: LogData):
    log_entry = APILog(
        api_key_id=log_data.api_key_id,
        endpoint=log_data.endpoint,
        status=log_data.status,
        client_ip_address=log_data.client_ip,
        user_agent=log_data.user_agent,
        request_body=log_data.request_body,
        error_message=log_data.error_message,
        response_time=log_data.response_time
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return
