"""Connection Module.

Description:
- This module is used to configure database connection and contains all tables.

"""

from datetime import datetime
from typing import Any, Unpack
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Engine, create_engine
from sqlalchemy.sql.functions import now
from sqlmodel import Field, MetaData, SQLModel
from sqlmodel.main import SQLModelMetaclass

from workshop_management_system.core.config import DATABASE_URL

engine: Engine = create_engine(url=DATABASE_URL)
my_metadata: MetaData = MetaData()


class CustomMetaclass(SQLModelMetaclass):
    """Custom Metaclass for BaseTable."""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Unpack[ConfigDict],
    ) -> Any:
        """Create new instance of BaseTable."""
        if bases and bases[0] is SQLModel and not kwargs.get("table"):
            return super().__new__(mcs, name, bases, namespace, **kwargs)

        if name != "BaseTable":
            # Remove 'Table' and convert to snake case
            namespace["__tablename__"] = "".join(
                f"_{c.lower()}" if c.isupper() else c
                for c in name.removesuffix("Table")
            ).lstrip("_")

        return super().__new__(mcs, name, bases, namespace, **kwargs)


# class BaseTable(SQLModel, metaclass=CustomMetaclass):
class BaseTable(SQLModel):
    """Base Table.

    Description:
    - This is base model for all tables.

    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime | None = Field(
        default=None, sa_column_kwargs={"onupdate": now()}
    )

    class BaseConfig:
        """Configuration for BaseTable."""

        arbitrary_types_allowed = True
