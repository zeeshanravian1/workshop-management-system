"""Base View Module.

Description:
- This module contains base view for all views in application.

"""

from collections.abc import Sequence
from typing import Generic, TypeVar

# from uuid import UUID
from sqlmodel import Session, select, update

from workshop_management_system.database.connection import Base

Model = TypeVar("Model", bound=Base)


class BaseView(Generic[Model]):
    """Base View Class.

    Description:
    - This class provides a generic CRUD interface for SQLModel models.

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

    def read_all(self, db_session: Session) -> Sequence[Model]:
        """Retrieve all records for model.

        :Args:
        - `db_session` (Session): SQLModel database session. **(Required)**

        :Returns:
        - `Sequence[Model]`: List of all records.

        """
        return db_session.exec(select(self.model)).all()

    def update(
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
        db_session.exec(
            statement=update(table=self.model)
            .where(self.model.id == record_id)  # type: ignore
            .values(record.model_dump(exclude_unset=True))
        )
        db_session.commit()

        return self.read_by_id(db_session=db_session, record_id=record_id)

    def delete(self, db_session: Session, record_id: int) -> Model | None:
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
            db_session.delete(record)
            db_session.commit()

        return record
