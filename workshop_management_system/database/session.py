"""Session Module.

Description:
- This module is used to configure database session.
"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlmodel import Session

from .connection import engine


@contextmanager
def get_session() -> Generator[Session]:
    """Get session.

    Description:
    - This function is used to get session.

    Returns:
    - **session** (Session): Database session.

    """
    session: Session = Session(bind=engine)

    try:
        yield session

    except Exception as err:
        session.rollback()
        raise err

    finally:
        session.close()
