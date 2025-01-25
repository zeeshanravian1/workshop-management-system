"""Test setup file for pytest.

Description:
- This file contains setup for tests. It creates a test database and session
for tests to use.
- Test database is created using DATABASE_URL with suffix "_test".
- Test database is dropped after tests are run.
- Session is disposed after tests are run.

"""

from collections.abc import Generator

import pytest
from sqlalchemy import Engine
from sqlalchemy_utils import create_database, database_exists, drop_database
from sqlmodel import Session, SQLModel, create_engine

from workshop_management_system.core.config import DATABASE_URL
from workshop_management_system.core.load_models import load_all_models
from workshop_management_system.v1.customer.model import Customer  # noqa: F401
from workshop_management_system.v1.vehicle.model import Vehicle  # noqa: F401


class TestSetup:
    """Test Setup Class.

    Description:
    - This class provides a setup for tests.

    Attributes:
    - `test_db_url` (str): A string representing test database URL.
    - `engine` (Engine): A SQLAlchemy engine object.
    - `session` (Session): A SQLAlchemy session object.

    """

    test_db_url: str
    engine: Engine
    session: Session

    @pytest.fixture(autouse=True)
    def setup(self) -> Generator[None, Session, None]:
        """Setup for tests.

        :Args:
        - `None`

        :Returns:
        - `None`

        """
        load_all_models()
        self.test_db_url = f"{DATABASE_URL}_test"

        if not database_exists(self.test_db_url):
            create_database(self.test_db_url)

        self.engine = create_engine(url=self.test_db_url)
        SQLModel.metadata.create_all(bind=self.engine)
        self.session = Session(bind=self.engine)

        yield

        self.session.close()
        drop_database(url=self.test_db_url)
        self.engine.dispose()
