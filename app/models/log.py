from sqlalchemy.orm import relationship
from app.config.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, null, Text
from sqlalchemy.sql import func


class APILog(Base):
    __tablename__ = 'api_logs'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    accessed_at = Column(DateTime, server_default=func.now())
    endpoint = Column(String)
    status = Column(Integer)
    api_key_id = Column(Integer, ForeignKey('api_keys.id'))
    request_body = Column(Text)
    client_ip_address = Column(String)
    error_message = Column(Text, default=null)
    response_time = Column(Integer)
    user_agent = Column(String)
    # Relationship to APIKey
    api_key = relationship("APIKey", back_populates="logs")
