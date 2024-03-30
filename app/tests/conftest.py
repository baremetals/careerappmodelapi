from datetime import datetime
import sys
import os
# from typing import Generator
import pytest
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
# from fastapi.testclient import TestClient
from career_app_model.config.core import config
from career_app_model.processing.data_manager import load_dataset

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.config.sendgrid_email import sg
from app.config.database import Base, get_db
from app.models.user import User
from app.config.guards import hash_password
from app.services.auth import _generate_tokens

USER_NAME = "Byron Mensah"
USER_EMAIL = "byron.mensah@test.com"
USER_PASSWORD = "Monkey0#!"

engine = create_engine("sqlite:///./fastapi.db")
DbTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    db = DbTesting()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def app_test():
    Base.metadata.create_all(bind=engine)
    yield app
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(app_test, test_session):
    def _test_db():
        try:
            yield test_session
        finally:
            pass

    app_test.dependency_overrides[get_db] = _test_db
    sg.config.SUPPRESS_SEND = 1
    return TestClient(app_test)


@pytest.fixture(scope="function")
def auth_client(app_test, test_session, user):
    def _test_db():
        try:
            yield test_session
        finally:
            pass

    app_test.dependency_overrides[get_db] = _test_db
    sg.config.SUPPRESS_SEND = 1
    data = _generate_tokens(user, test_session)
    client = TestClient(app_test)
    client.headers['Authorization'] = f"Bearer {data['access_token']}"
    return client


@pytest.fixture(scope="function")
def inactive_user(test_db):
    model = User()
    model.name = USER_NAME
    model.email = USER_EMAIL
    model.password = hash_password(USER_PASSWORD)
    model.updated_at = datetime.utcnow()
    model.is_active = False
    test_db.add(model)
    test_db.commit()
    test_db.refresh(model)
    return model


@pytest.fixture(scope="function")
def user(test_db):
    model = User()
    model.name = USER_NAME
    model.email = USER_EMAIL
    model.password = hash_password(USER_PASSWORD)
    model.updated_at = datetime.utcnow()
    model.verified_at = datetime.utcnow()
    model.is_active = True
    test_db.add(model)
    test_db.commit()
    test_db.refresh(model)
    return model


@pytest.fixture(scope="function")
def unverified_user(test_db):
    model = User()
    model.name = USER_NAME
    model.email = USER_EMAIL
    model.password = hash_password(USER_PASSWORD)
    model.updated_at = datetime.utcnow()
    model.is_active = True
    test_db.add(model)
    test_db.commit()
    test_db.refresh(model)
    return model


@pytest.fixture(scope="module")
def test_data() -> pd.DataFrame:
    return load_dataset(file_name=config.app_config.test_data_file)

# @pytest.fixture()
# def client() -> Generator:
#     with TestClient(app) as _client:
#         yield _client
#         app.dependency_overrides = {}
