import databases
import sqlalchemy

from config import get_settings

# Settings dependency.
settings = get_settings()

# SQLite database.
database = databases.Database(settings.DATABASE_URL)

# Resource table.
metadata = sqlalchemy.MetaData()
resources = sqlalchemy.Table(
    "resource",
    metadata,
    sqlalchemy.Column("iri", sqlalchemy.Text, primary_key=True),
    sqlalchemy.Column("hash", sqlalchemy.LargeBinary(length=32), primary_key=True),
    sqlalchemy.Column("data", sqlalchemy.Text)
)