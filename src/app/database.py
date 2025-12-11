import datetime
import os

from sqlalchemy import DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)


class Base(DeclarativeBase):
    pass


class ForwardCall(Base):
    __tablename__ = "forward_call"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime(), nullable=False)
    finish_time: Mapped[datetime.datetime] = mapped_column(DateTime(), nullable=False)
