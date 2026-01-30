import os
import sys
from dotenv import load_dotenv
load_dotenv()
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "src")))

config = context.config

if env_url := os.getenv("DATABASE_URL"):
    config.set_main_option("sqlalchemy.url", env_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from core.db import Base
from common.models import *


target_metadata = Base.metadata

def include_object(object, name, type_, reflected, compare_to):
    """
    Ignore all tables in the 'cron' schema and spatial metadata tables.
    """
    if type_ == "table":
        # ignore cron schema tables
        if object.schema == "cron":
            return False
        # ignore PostGIS metadata tables
        if name in {"spatial_ref_sys", "geometry_columns", "geography_columns", "raster_columns", "raster_overviews"}:
            return False
    return True



def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas = True,
        include_object=include_object, 
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            include_schemas = True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
