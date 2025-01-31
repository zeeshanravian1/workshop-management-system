"""Connection Module.

Description:
- This module is used to configure database connection and contains all tables.

"""

from datetime import datetime

# from uuid import UUID, uuid4
from sqlalchemy import Engine
from sqlalchemy.sql.functions import now
from sqlmodel import Field, MetaData, SQLModel, create_engine

from workshop_management_system.core.config import DATABASE_URL

engine: Engine = create_engine(url=DATABASE_URL)
my_metadata: MetaData = MetaData()


class Base(SQLModel):
    """Base Table.

    Description:
    - This is base model for all tables.

    """

    # id: UUID = Field(default_factory=uuid4, primary_key=True)
    id: int = Field(primary_key=True)
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime | None = Field(
        default=None, sa_column_kwargs={"onupdate": now()}
    )

    class BaseConfig:  # pylint: disable=too-few-public-methods
        """Configuration for BaseTable."""

        arbitrary_types_allowed = True
