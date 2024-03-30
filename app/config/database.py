from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config.settings import get_settings
from typing import Generator

settings = get_settings()

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URI
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:YcLFQiVMcgRU3zk@localhost/careerappmodelapi'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
