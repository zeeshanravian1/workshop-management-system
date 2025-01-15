"""Session Module.

Description:
- This module is used to configure database session.

"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session, sessionmaker

from .connection import engine

session_local = sessionmaker(
    autoflush=True, bind=engine, expire_on_commit=True
)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get session.

    Description:
    - This function is used to get session.

    Returns:
    - **session** (Session): Database session.

    """
    session: Session = session_local()

    try:
        yield session

    except Exception as err:
        session.rollback()
        raise err

    finally:
        session.close()
