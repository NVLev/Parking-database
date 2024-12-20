import os
import sys
from datetime import date, datetime

import pytest
from flask import template_rendered

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import date, datetime

import pytest

from application.app import create_app
from config import Config
from models.model import Base, Client, ClientParking, Parking
from models.model import db as _db  # Rename db to _db
from models.model import is_parking_open


@pytest.fixture(scope="session")
def app():
    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
    with _app.app_context():
        _db.drop_all()
        _db.create_all()
        yield _app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.session.begin(nested=True)  # Allow nested transactions
        yield _db
        _db.session.rollback()  # Removed this line


@pytest.fixture(scope="function")
def app_client(app):
    app_client = app.test_client()
    yield app_client
