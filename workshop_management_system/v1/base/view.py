"""Base View Module.

Description:
- This module contains base view for all views in application.

"""

from collections.abc import Sequence
from typing import Generic

from sqlalchemy import ColumnElement
from sqlmodel import Session, col, func, select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from .model import Message, Model, PaginationBase


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

    def create_multiple(
        self, db_session: Session, records: Sequence[Model]
    ) -> Sequence[Model]:
        """Create multiple records in database.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `records` (Sequence[Model]): List of Model objects to be added to
        database. **(Required)**

        :Returns:
        - `Sequence[Model]`: List of created records.

        """
        db_session.add_all(instances=records)
        db_session.commit()

        return records

    def read_by_id(self, db_session: Session, record_id: int) -> Model | None:
        """Retrieve a record by its ID.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_id` (UUID | int): ID of record. **(Required)**

        :Returns:
        - `Model | None`: Retrieved record, or None if not found.

        """
        return db_session.get(entity=self.model, ident=record_id)

    def read_multiple_by_ids(
        self, db_session: Session, record_ids: Sequence[int]
    ) -> Sequence[Model]:
        """Retrieve multiple records by their IDs.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_ids` (Sequence[UUID | int]): List of record IDs.
        **(Required)**

        :Returns:
        - `Sequence[Model]`: List of retrieved records.

        """
        query: SelectOfScalar[Model] = select(self.model).where(
            col(column_expression=self.model.id).in_(other=record_ids)
        )
        return db_session.exec(statement=query).all()

    def read_all(
        self,
        db_session: Session,
        page: int = 1,
        limit: int = 10,
        search_by: str | None = None,
        search_query: str | None = None,
    ) -> PaginationBase[Model]:
        """Retrieve paginated records for model.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `page` (int): Page number to fetch. **(Optional)**
        - `limit` (int): Maximum number of records per page. **(Optional)**
        - `search_by` (str): Field to search by. **(Optional)**
        - `search_query` (str): Query string for search. **(Optional)**

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
        # Validate search column
        if search_by and not hasattr(self.model, search_by):
            raise ValueError("Invalid search column")

        # Build search condition
        search_condition: ColumnElement[bool] | None = (
            col(column_expression=getattr(self.model, search_by)).contains(
                other=search_query
            )
            if search_by and search_query
            else None
        )

        # Get total count and calculate pages
        count_query: SelectOfScalar[int] = select(
            func.count()  # pylint: disable=not-callable
        ).select_from(self.model)

        if search_condition is not None:
            count_query = count_query.where(search_condition)

        total_records: int = db_session.exec(statement=count_query).one()
        total_pages: int = max(1, (total_records + limit - 1) // limit)

        # Validate and adjust page number
        page = min(max(1, page), total_pages)

        # Return if no records
        if total_records == 0:
            return PaginationBase(
                current_page=page,
                limit=limit,
                total_pages=total_pages,
                total_records=total_records,
                next_record_id=None,
                previous_record_id=None,
                records=[],
            )

        # Calculate cursor
        cursor: int | None = (page - 1) * limit if page > 1 else None

        # Build main query with all conditions
        query: SelectOfScalar[Model] = (
            select(self.model)
            .order_by(self.model.id)  # type: ignore
            .limit(limit=limit)
        )

        if search_condition is not None:
            query = query.where(search_condition)

        if cursor:
            query = query.where(self.model.id > cursor)

        # Execute query
        records: Sequence[Model] = db_session.exec(statement=query).all()

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

    def update_multiple_by_ids(
        self,
        db_session: Session,
        record_ids: Sequence[int],
        records: Sequence[Model],
    ) -> Sequence[Model]:
        """Update multiple records by their IDs.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_ids` (Sequence[UUID | int]): List of record IDs.
        **(Required)**
        - `records` (Sequence[Model]): List of Model objects containing updated
        fields. **(Required)**

        :Returns:
        - `Sequence[Model]`: List of updated records.

        """
        db_records: Sequence[Model] = self.read_multiple_by_ids(
            db_session=db_session, record_ids=record_ids
        )

        for db_record, record in zip(db_records, records, strict=False):
            db_record.sqlmodel_update(
                obj=record.model_dump(exclude_unset=True)
            )

        db_session.commit()

        return db_records

    def delete_by_id(
        self, db_session: Session, record_id: int
    ) -> Message | None:
        """Delete a record by its ID.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_id` (UUID | int): ID of record to delete. **(Required)**

        :Returns:
        - `Message | None`: Message indicating that the record has been
        deleted, or None if not found.

        """
        record: Model | None = db_session.get(
            entity=self.model, ident=record_id
        )

        if not record:
            return None

        db_session.delete(instance=record)
        db_session.commit()

        return Message(message="Record deleted successfully")

    def delete_multiple_by_ids(
        self, db_session: Session, record_ids: Sequence[int]
    ) -> Message | None:
        """Delete multiple records by their IDs.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**
        - `record_ids` (Sequence[UUID | int]): List of record IDs.
        **(Required)**

        :Returns:
        - `None`: Indicates that the records have been deleted.

        """
        records: Sequence[Model] = self.read_multiple_by_ids(
            db_session=db_session, record_ids=record_ids
        )

        for record in records:
            db_session.delete(instance=record)

        db_session.commit()

        return Message(message="Records deleted successfully")
