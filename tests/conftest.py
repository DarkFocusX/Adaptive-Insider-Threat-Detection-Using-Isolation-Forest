"""Shared test fixtures."""

import os
import tempfile

import pytest

from app import create_app
from database.create_tables import create_tables


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    class TestConfig:
        TESTING = True
        SECRET_KEY = "test-secret"
        DATABASE_PATH = db_path
        UPLOAD_FOLDER = tempfile.mkdtemp()
        LOG_FOLDER = tempfile.mkdtemp()
        MODEL_PATH = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "ml_model",
            "trained_model.pkl",
        )
        OPENING_BALANCE = 1000.0
        DEFAULT_TRUST_SCORE = 95.0

    application = create_app(TestConfig)
    with application.app_context():
        create_tables(db_path)
    yield application

    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()
