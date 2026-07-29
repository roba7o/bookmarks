import uuid

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    MetaData,
    Table,
    Text,
    text,
)

# -------- Postgres alchemy Schemas ------------

# Table instantiation - postgressqlalchemy
metadata = MetaData()

# bookmarks only need to be unique for a user, two users can have the same bookmark
bookmarks_table = Table(
    "bookmarks",
    metadata,
    Column("bm_seq", Integer, Identity(always=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False),
    Column("title", Text, unique=True),
    Column("author", Text),
    Column("page", Integer),
    Column(
        "created_at",
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    ),
)


user_table = Table(
    "users",
    metadata,
    Column("email", Text, unique=True, nullable=False),
    Column(
        "user_id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    ),
    Column("hashed_pw", Text, nullable=False),
    Column(
        "created_at",
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False,
    ),
)


# -------- Pydantic Schemas ------------


class BookMarkCreate(BaseModel):
    title: str
    author: str
    page: int


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=20)


class LoginRequest(BaseModel):
    email: str
    password: str
