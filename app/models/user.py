from sqlalchemy.orm import relationship, mapped_column
from app.config.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from datetime import datetime
from sqlalchemy.sql import func


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)
    company_name = Column(String)
    verified_at = Column(DateTime, nullable=True, default=None)
    updated_at = Column(DateTime, nullable=True, default=None, onupdate=datetime.now)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    user_status = Column(String)
    user_role = Column(String, default='user')
    # Relationship to API Key
    api_key = relationship("APIKey", back_populates="user")
    tokens = relationship("UserToken", back_populates="user")

    def get_context_string(self, context: str):
        return f"{context}{self.password[-6:]}{self.updated_at.strftime('%m%d%Y%H%M%S')}".strip()


class APIKey(Base):
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    key = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    isActive = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    user_id = Column(Integer, ForeignKey('users.id'))

    # Relationship to User
    user = relationship("User", back_populates="api_key")
    logs = relationship("APILog", back_populates="api_key")


class UserToken(Base):
    __tablename__ = "user_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(ForeignKey('users.id'))
    access_key = Column(String(250), nullable=True, index=True, default=None)
    refresh_key = Column(String(250), nullable=True, index=True, default=None)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="tokens")
