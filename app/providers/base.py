from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class VacancyDTO:
    """Нормализованная вакансия, готовая к записи в модель."""
    hh_id: str
    title: str
    company: str | None
    url: str
    area: str | None
    salary_from: int | None
    salary_to: int | None
    currency: str | None
    has_phone: bool
    phone: str | None
    contact_name: str | None
    published_at: datetime | None
    raw_json: dict


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt)
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    logger.warning("Не удалось разобрать дату: %r", value)
    return None
