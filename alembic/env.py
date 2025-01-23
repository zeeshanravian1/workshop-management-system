"""Migration script for database.

Description:
- This script is used to run migrations for database.

"""

from importlib import import_module
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import Engine, MetaData, engine_from_config, pool

from alembic.config import Config
from alembic.context import (
    begin_transaction,
    config,
    configure,
    is_offline_mode,
    run_migrations,
)
from workshop_management_system.core.config import DATABASE_URL
from workshop_management_system.database.connection import my_metadata


def load_all_models() -> None:
    """Load SQLAlchemy models from project."""
    base_path: Path = Path(__file__).resolve().parent.parent

    # Discover all Python files in project
    for path in base_path.rglob(pattern="*.py"):
        if "site-packages" in str(object=path):
            continue

        try:
            # Import module
            import_module(
                name=".".join(
                    path.relative_to(base_path).with_suffix(suffix="").parts
                )
            )
        except ModuleNotFoundError:
            continue


load_all_models()


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config: Config = config  # pylint: disable=E1101

config.set_main_option(name="sqlalchemy.url", value=DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(fname=config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata: MetaData = my_metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url: str | None = config.get_main_option(name="sqlalchemy.url")
    configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with begin_transaction():
        run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable: Engine = engine_from_config(
        configuration=config.get_section(
            name=config.config_ini_section, default={}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        configure(connection=connection, target_metadata=target_metadata)

        with begin_transaction():
            run_migrations()


if is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
