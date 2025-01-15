"""Connection Module.

Description:
- This module is used to configure database connection and contains all tables.

"""

from typing import Any

from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

from workshop_management_system.core.config import DATABASE_URL

engine: Engine = create_engine(url=DATABASE_URL)
my_metadata: MetaData = MetaData()


class BaseTable(DeclarativeBase):
    """Base Table.

    Description:
    - This is base model for all tables.

    """

    __abstract__ = True
    metadata: MetaData = my_metadata  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    @declared_attr.directive
    def __tablename__(self) -> str:
        """Generate table name automatically."""
        return (
            "".join(
                f"_{c.lower()}" if c.isupper() else c for c in self.__name__
            )
            .lstrip("_")
            .removesuffix("_table")
        )

    # Convert to dictionary
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
