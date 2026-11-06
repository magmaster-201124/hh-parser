from datetime import datetime, timezone

from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    hh_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str | None] = mapped_column(String(512))
    company: Mapped[str | None] = mapped_column(String(256))
    url: Mapped[str] = mapped_column(String(512))
    area: Mapped[str | None] = mapped_column(String(128))
    salary_from: Mapped[int | None] = mapped_column(Integer)
    salary_to: Mapped[int | None] = mapped_column(Integer)
    currency: Mapped[str | None] = mapped_column(String(8))
    has_phone: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32))
    contact_name: Mapped[str | None] = mapped_column(String(256))
    raw_json: Mapped[dict | None] = mapped_column(JSONB)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
