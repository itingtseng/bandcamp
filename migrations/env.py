from __future__ import with_statement

import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os

# Environment and schema variables
environment = os.getenv("FLASK_ENV", "development")  # Default to 'development' if not set
SCHEMA = os.getenv("SCHEMA", "public")  # Default to 'public' schema if not set

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Set up SQLAlchemy URL from Flask app
from flask import current_app
config.set_main_option(
    'sqlalchemy.url',
    str(current_app.extensions['migrate'].db.engine.url).replace('%', '%%')
)

# Target metadata for autogenerate support
target_metadata = current_app.extensions['migrate'].db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )

    logger.info("Running migrations in offline mode.")
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""

    # Callback to handle empty revisions
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    # Create engine and connect
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Configure migration context
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            **current_app.extensions['migrate'].configure_args
        )

        # Create schema and set search path in production
        if environment == "production":
            logger.info(f"Ensuring schema '{SCHEMA}' exists.")
            connection.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
            logger.info(f"Setting search_path to '{SCHEMA}'.")
            connection.execute(f"SET search_path TO {SCHEMA}")

        # Run migrations
        logger.info("Running migrations in online mode.")
        with context.begin_transaction():
            context.run_migrations()


# Determine offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
