"""Base View Module.

Description:
- This module contains base view for all views in application.

"""

from collections.abc import Sequence
from typing import Generic

from sqlmodel import Session, func, select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from .model import Model, PaginationBase


class BaseView(Generic[Model]):
    """Base View Class.

    Description:
    - This class provides a generic CRUD interface for database models.

    """

    def __init__(self, model: type[Model]) -> None:
        """Initialize BaseView.

        :Args:
        - `model` (Type[Model]): SQLModel model class. **(Required)**

        :Returns:
        - `None`

        """
        self.model: type[Model] = model

    def create(self, db_session: Session, record: Model) -> Model:
        """Create a new record in database.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record` (Model): Model object to be added to database.
        **(Required)**

        :Returns:
        - `Model`: Created record.

        """
        db_session.add(instance=record)
        db_session.commit()
        db_session.refresh(instance=record)

        return record

    def read_by_id(self, db_session: Session, record_id: int) -> Model | None:
        """Retrieve a record by its ID.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_id` (UUID | int): ID of record. **(Required)**

        :Returns:
        - `Model | None`: Retrieved record, or None if not found.

        """
        return db_session.get(entity=self.model, ident=record_id)

    def read_all(
        self, db_session: Session, page: int = 1, limit: int = 10
    ) -> PaginationBase[Model]:
        """Retrieve paginated records for model.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `page` (int): Page number to fetch. **(Optional)**
        - `limit` (int): Maximum number of records per page. **(Optional)**

        :Returns:
        - `PaginationBase`: Object containing:
            - `current_page (int)`: Current page number.
            - `limit (int)`: Records per page.
            - `total_pages (int)`: Total number of pages.
            - `total_records (int)`: Total number of records.
            - `next_record_id (int)`: ID of first record on next page (None if
            last page)
            - `previous_record_id (int)`: ID of first record on previous page
            (None if first page)
            - `records (list[Model])`: List of records for current page.

        """
        # Get total count and calculate pages
        total_records: int = db_session.exec(
            select(func.count()).select_from(  # pylint: disable=not-callable
                self.model
            )
        ).one()
        total_pages: int = max(1, (total_records + limit - 1) // limit)

        # Validate and adjust page number
        page = min(max(1, page), total_pages)

        # Calculate cursor
        cursor: int | None = (page - 1) * limit if page > 1 else None

        # Build and execute query
        query: SelectOfScalar[Model] = (
            select(self.model)
            .order_by(self.model.id)  # type: ignore
            .limit(limit)
        )

        if cursor:
            query = query.where(self.model.id > cursor)

        records: Sequence[Model] = db_session.exec(query).all()

        # Calculate cursors
        next_cursor: int | None = (
            records[-1].id + 1 if page * limit < total_records else None
        )
        previous_cursor: int | None = (
            max(1, ((page - 2) * limit) + 1) if page > 1 else None
        )

        return PaginationBase(
            current_page=page,
            limit=limit,
            total_pages=total_pages,
            total_records=total_records,
            next_record_id=next_cursor,
            previous_record_id=previous_cursor,
            records=records,
        )

    def update_by_id(
        self, db_session: Session, record_id: int, record: Model
    ) -> Model | None:
        """Update a record by its ID.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_id` (int): ID of record to update. **(Required)**
        - `record` (Model): Model containing updated fields. **(Required)**

        :Returns:
        - `Model | None`: Updated record, or None if not found.

        """
        db_record: Model | None = self.read_by_id(
            db_session=db_session, record_id=record_id
        )

        if not db_record:
            return None

        db_record.sqlmodel_update(obj=record.model_dump(exclude_unset=True))
        db_session.commit()
        db_session.refresh(instance=db_record)

        return db_record

    def delete_by_id(
        self, db_session: Session, record_id: int
    ) -> Model | None:
        """Delete a record by its ID.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_id` (UUID | int): ID of record to delete. **(Required)**

        :Returns:
        - `Model | None`: Deleted record, or None if not found.

        """
        record: Model | None = db_session.get(
            entity=self.model, ident=record_id
        )

        if record:
            db_session.delete(instance=record)
            db_session.commit()

        return record
