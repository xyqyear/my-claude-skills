# Alembic Database Migrations

Optional feature for the fullstack scaffold. Read this file when the user requests database migrations.

## Installation

```bash
cd backend
uv add alembic
```

## Initialization

Use the async template:

```bash
cd backend
alembic init -t async alembic
```

This creates:

```
backend/
├── alembic.ini
└── alembic/
    ├── env.py
    ├── script.py.mako
    └── versions/
```

## Configuration

### alembic.ini

Set the database URL and enable meaningful revision IDs:

```ini
[alembic]
script_location = alembic
sqlalchemy.url = sqlite+aiosqlite:///./data/db.sqlite3

# Enable process_revision_directives for ALL revision commands (not just --autogenerate)
revision_environment = true

# File naming: date prefix + sequential ID + slug
file_template = %%(year)d_%%(month).2d_%%(day).2d-%%(rev)s_%%(slug)s
```

### alembic/env.py

Replace the generated `env.py` with this version that supports:
- Sequential numeric revision IDs (not random hex)
- SQLite batch mode (`render_as_batch=True`)
- Foreign key PRAGMA handling
- Programmatic execution from FastAPI lifespan via `config.attributes["connection"]`

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from alembic.script import ScriptDirectory

from app.config import settings
from app.models import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def process_revision_directives(context, revision, directives):
    """Generate sequential numeric revision IDs (0001, 0002, ...) instead of random hex."""
    migration_script = directives[0]
    head_revision = ScriptDirectory.from_config(context.config).get_current_head()

    if head_revision is None:
        new_rev_id = 1
    else:
        last_rev_id = int(head_revision.lstrip("0") or "0")
        new_rev_id = last_rev_id + 1

    migration_script.rev_id = f"{new_rev_id:04d}"


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        render_as_batch=True,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    if connection.dialect.name == "sqlite":
        connection.execute(text("PRAGMA foreign_keys=OFF"))

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
        compare_type=True,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()

    if connection.dialect.name == "sqlite":
        connection.execute(text("PRAGMA foreign_keys=ON"))


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    connectable = config.attributes.get("connection", None)

    if connectable is None:
        asyncio.run(run_async_migrations())
    else:
        do_run_migrations(connectable)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Custom Revision IDs

The `process_revision_directives` hook generates sequential IDs: `0001`, `0002`, `0003`, etc.

Combined with the `file_template` setting, migration files look like:

```
versions/
├── 2026_03_03-0001_create_items_table.py
├── 2026_03_15-0002_add_user_model.py
└── 2026_04_01-0003_add_email_to_users.py
```

The `revision_environment = true` setting in `alembic.ini` is critical — without it, the hook only fires with `--autogenerate`, and manual `alembic revision` commands produce random hex IDs.

Note: Alembic determines migration ordering by the `down_revision` linked list, not by the ID values. Sequential IDs are for human readability only.

## Replace init_db() with Alembic

When Alembic is enabled, update `app/db.py` to run migrations instead of `create_all`:

```python
from alembic import command
from alembic.config import Config


def _run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


async def init_db() -> None:
    db_path = settings.database_url.split("///")[-1]
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", settings.database_url)

    async with engine.begin() as conn:
        await conn.run_sync(_run_upgrade, cfg)
```

This passes the existing async connection to Alembic via `config.attributes["connection"]`, avoiding the event loop conflict that occurs when `asyncio.run()` is called inside an already-running loop (like FastAPI's lifespan).

## Common Commands

```bash
# Create a migration (autogenerate from model changes)
alembic revision --autogenerate -m "create items table"

# Create a manual migration
alembic revision -m "add seed data"

# Apply all pending migrations
alembic upgrade head

# Downgrade one step
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history --verbose

# Generate SQL without applying
alembic upgrade head --sql
```

## Initial Migration Workflow

After setting up Alembic, create the first migration:

```bash
cd backend
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

## SQLite-Specific Notes

- `render_as_batch=True` is required — SQLite cannot `ALTER TABLE` to drop columns, add constraints, etc. Batch mode works around this by recreating tables.
- Foreign keys must be disabled during batch migrations (handled in `env.py` above).
- The `naming_convention` on `Base.metadata` (defined in `models.py`) is required so that constraints have predictable names for batch operations.
