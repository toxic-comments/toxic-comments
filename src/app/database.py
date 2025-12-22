import datetime
import os
from enum import Enum

from sqlalchemy import DateTime, Text, String
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/toxic-comments")

engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass

class PredictedClass(str, Enum):
    INSULT = "INSULT"
    NORMAL = "NORMAL"
    OBSCENITY = "OBSCENITY"
    THREAT = "THREAT"
    UNKNOWN = "UNKNOWN" # нужно для обратной совместимости с запросами, сохраненными ранее

class ForwardCall(Base):
    __tablename__ = "forward_call"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime(), nullable=False)
    finish_time: Mapped[datetime.datetime] = mapped_column(DateTime(), nullable=False)
    message: Mapped[str] = mapped_column(Text()) 
    result: Mapped[PredictedClass] = mapped_column(String)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(
    String(100),
    nullable=False,
    unique=True)

    password_hash: Mapped[str] = mapped_column(
    String(255),
    nullable=False)

    role: Mapped[str] = mapped_column(
    String(50),
    nullable=False,
    default="user")
