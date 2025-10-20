"""
Database setup for the FastAPI mini-blog.

Responsibilities:
- Define the SQLite connection URL and async Database instance.
- Declare SQLAlchemy Core table metadata for users, posts, and comments.
- Provide a single source of truth for table objects used by route handlers.
"""


# === Imports & Setup =========================================================
import databases
import sqlalchemy

# === Database URL & engine/metadata =========================================
DATABASE_URL = "sqlite:///data.db"  # could come from an env var
metadata = sqlalchemy.MetaData()
# === Async Database instance =================================================
database = databases.Database(DATABASE_URL)


# === Table definitions =======================================================
# Users: stores account credentials (username, password hash)
user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),          # PK
    sqlalchemy.Column("username", sqlalchemy.String(30)),
    sqlalchemy.Column("password", sqlalchemy.String)
)


# Posts: text payload per post; linked to the authenticated user
posts = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),          # PK
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False)   # FK → users.id
)


# Comments: text payload linked to a post and user
comments_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),          # PK
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id"), nullable=False),   # FK → posts.id
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),   # FK → users.id
)


# === Engine & metadata creation =============================================
engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)
