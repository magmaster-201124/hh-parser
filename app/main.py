from __future__ import annotations

import logging
from dataclasses import asdict

from sqlalchemy.orm import Session

from .config import HH_AREA, HH_QUERY, MAX_PAGES, TRUDVSEM_QUERY
from .db import SessionLocal
from .models import Vacancy
from .providers.base import SourceUnavailableError, VacancyDTO
from .providers.hh import fetch_hh
from .providers.trudvsem import fetch_vacancies

logger = logging.getLogger(__name__)


def upsert_vacancies(session: Session, items: list[VacancyDTO]) -> tuple[int, int]:
    """Пишет вакансии в БД. Возвращает (создано, обновлено)."""
    created = updated = 0
    for dto in items:
        obj = session.get(Vacancy, dto.hh_id)
        if obj is None:
            session.add(Vacancy(**asdict(dto)))
            created += 1
        else:
            for field, value in asdict(dto).items():
                setattr(obj, field, value)
            updated += 1
    session.commit()
    return created, updated


def run() -> None:
    items = fetch_vacancies(TRUDVSEM_QUERY, MAX_PAGES)
    try:
        items += fetch_hh(HH_QUERY, HH_AREA, MAX_PAGES)
    except SourceUnavailableError as exc:
        logger.warning("Пропускаю источник hh: %s", exc)
    with SessionLocal() as session:
        created, updated = upsert_vacancies(session, items)
    with_phone = sum(1 for dto in items if dto.has_phone)
    logger.info(
        "Итог: собрано %d, новых %d, обновлено %d, с телефоном %d",
        len(items),
        created,
        updated,
        with_phone,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s %(name)s: %(message)s"
    )
    run()
