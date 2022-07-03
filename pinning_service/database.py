import databases
import sqlalchemy

from .config import get_settings

# Settings dependency.
settings = get_settings()

# Build the database object.
# Do not persist database changes for tests. Rollback transactions once the database is disconnected.
database = databases.Database(settings.SQLALCHEMY_DATABASE_URI, force_rollback=settings.TESTING)

# Resource table.
metadata = sqlalchemy.MetaData()
resources = sqlalchemy.Table(
    "resource",
    metadata,
    sqlalchemy.Column("iri", sqlalchemy.Text, primary_key=True),
    sqlalchemy.Column("hash", sqlalchemy.LargeBinary(length=32), primary_key=True),
    sqlalchemy.Column("data", sqlalchemy.Text),
    sqlalchemy.Column("txhash", sqlalchemy.Text),
    sqlalchemy.Column("anchor_attempts", sqlalchemy.Integer),
    sqlalchemy.Column("pinned_at", sqlalchemy.DateTime),
    sqlalchemy.Column("anchored_at", sqlalchemy.DateTime),
)


def create_tables():
    engine = sqlalchemy.create_engine(
        settings.SQLALCHEMY_DATABASE_URI
    )
    metadata.create_all(engine)
