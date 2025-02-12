"""Connection Module.

Description:
- This module is used to configure database connection and contains base table
for all tables.

"""

from datetime import datetime

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

    :Attributes:
    - `id (int)`: Primary key for all tables.
    - `created_at (datetime)`: Timestamp when record was created.
    - `updated_at (datetime | None)`: Timestamp when record was last updated.

    """

    id: int = Field(primary_key=True)
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime | None = Field(
        default=None, sa_column_kwargs={"onupdate": now()}
    )

    class ModelConfig:
        """Configuration for BaseTable."""

        str_strip_whitespace = True
