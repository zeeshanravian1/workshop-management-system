"""Base View Module.

Description:
- This module contains the base view for all the views in the application.

"""

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session
from sqlalchemy.sql import delete, update

from workshop_management_system.database.connection import BaseTable

Model = TypeVar("Model", bound=BaseTable)


class BaseView(Generic[Model]):
    """Base View Class.

    Description:
    - This class provides a generic CRUD interface for SQLAlchemy models.

    """

    def __init__(self, model: type[Model]) -> None:
        """Initialize the BaseView.

        :Args:
        - `model` (Type[Model]): SQLAlchemy model class. **(Required)**

        :Returns:
        - `None`

        """
        self.model: type[Model] = model

    def create(
        self, db_session: Session, record_data: dict[str, Any]
    ) -> Model:
        """Create a new record in the database.

        :Args:
        - `db_session` (Session): SQLAlchemy database session. **(Required)**
        - `record_data` (dict[str, Any]): Data for the new record.
        **(Required)**

        :Returns:
        - `Model`: The created record.

        """
        record: Model = self.model(**record_data)
        db_session.add(instance=record)
        db_session.commit()
        db_session.refresh(instance=record)

        return record

    def read_by_id(self, db_session: Session, record_id: int) -> Model | None:
        """Retrieve a record by its ID.

        :Args:
        - `db_session` (Session): SQLAlchemy database session. **(Required)**
        - `record_id` (int): ID of the record. **(Required)**

        :Returns:
        - `Model | None`: The retrieved record, or None if not found.

        """
        return db_session.query(self.model).get(ident=record_id)

    def read_all(self, db_session: Session) -> Sequence[Model]:
        """Retrieve all records for the model.

        :Args:
        - `db_session` (Session): SQLAlchemy database session. **(Required)**

        :Returns:
        - `Sequence[Model]`: List of all records.

        """
        return db_session.query(self.model).all()

    def update(
        self, db_session: Session, record_id: int, record_data: dict[str, Any]
    ) -> Model | None:
        """Update a record by its ID.

        :Args:
        - `db_session` (Session): SQLAlchemy database session. **(Required)**
        - `record_id` (int): ID of the record to update. **(Required)**
        - `record_data` (dict[str, Any]): Data to update. **(Required)**

        :Returns:
        - `Model | None`: The updated record, or None if not found.

        """
        db_session.execute(
            statement=update(table=self.model)
            .where(self.model.id == record_id)
            .values(**record_data)
        )
        db_session.commit()

        return self.read_by_id(db_session=db_session, record_id=record_id)

    def delete(self, db_session: Session, record_id: int) -> Model | None:
        """Delete a record by its ID.

        :Args:
        - `db_session` (Session): SQLAlchemy database session. **(Required)**
        - `record_id` (int): ID of the record to delete. **(Required)**

        :Returns:
        - `Model | None`: The deleted record, or None if not found.

        """
        record: Model | None = self.read_by_id(
            db_session=db_session, record_id=record_id
        )

        if not record:
            return None

        db_session.execute(
            statement=delete(table=self.model).where(
                self.model.id == record_id
            )
        )
        db_session.commit()

        return record
