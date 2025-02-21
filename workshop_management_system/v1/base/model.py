"""Base Model.

Description:
- This module contains model for base.

"""

from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlmodel import Field, SQLModel

from workshop_management_system.database.connection import Base

Model = TypeVar("Model", bound=Base)


class Message(SQLModel):
    """Message Model.

    Description:
    - This class contains model for message.

    :Attributes:
    - `message (str)`: Message.

    """

    message: str


class PaginationBase(SQLModel, Generic[Model]):
    """Pagination Base Model.

    Description:
    - This class contains base model for pagination.

    :Attributes:
    - `current_page (int)`: Current page number.
    - `limit (int)`: Records per page.
    - `total_pages (int)`: Total number of pages.
    - `total_records (int)`: Total number of records.
    - `next_record_id (int)`: ID of first record on next page (None if last
    page)
    - `previous_record_id (int)`: ID of first record on previous page (None if
    first page)
    - `records (list[Model])`: List of records for current page.

    """

    current_page: int = Field(default=1, gt=0)
    limit: int = Field(default=10, gt=0)
    total_pages: int = Field(default=0)
    total_records: int = Field(default=0)
    next_record_id: int | None = Field(default=None, gt=0)
    previous_record_id: int | None = Field(default=None, gt=0)
    records: Sequence[Model] = Field(default=[])
