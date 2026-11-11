from __future__ import annotations

import logging

import requests

from app.config import HH_API_TOKEN

from .base import SourceUnavailableError, VacancyDTO, parse_dt

BASE_URL = "https://api.hh.ru/vacancies"
HEADERS: dict[str, str] = {"User-Agent": "Resumetto-parser/1.0 (test task)"}
PAGE_LIMIT = 100
REQUEST_TIMEOUT = 30

logger = logging.getLogger(__name__)


def _headers() -> dict[str, str]:
    h = dict(HEADERS)
    if HH_API_TOKEN:
        h["Authorization"] = f"Bearer {HH_API_TOKEN}"
    return h


def normalize_hh(item: dict) -> VacancyDTO | None:
    """Превращает сырой элемент выдачи hh.ru в DTO."""
    vac_id = str(item.get("id") or "").strip()
    if not vac_id:
        logger.warning("Вакансия hh без id, пропущена")
        return None

    salary = item.get("salary") or {}
    contacts = item.get("contacts") or {}
    phone = None
    for p in contacts.get("phones") or []:
        formatted = p.get("formatted") or "".join(
            filter(None, (p.get("city"), p.get("number")))
        )
        if formatted:
            phone = formatted
            break

    return VacancyDTO(
        hh_id=vac_id,
        title=item.get("name") or "",
        company=(item.get("employer") or {}).get("name"),
        url=item.get("alternate_url") or "",
        area=(item.get("area") or {}).get("name"),
        salary_from=salary.get("from"),
        salary_to=salary.get("to"),
        currency=salary.get("currency"),
        has_phone=phone is not None,
        phone=phone,
        contact_name=(contacts.get("name") or "").strip() or None,
        published_at=parse_dt(item.get("published_at")),
        raw_json=item,
    )


def fetch_hh(query: str, area: int, pages: int = 1) -> list[VacancyDTO]:
    """Собирает вакансии hh.ru постранично, останавливается по found."""
    items: list[VacancyDTO] = []
    for page in range(max(pages, 1)):
        params: dict[str, str | int] = {
            "text": query,
            "area": area,
            "per_page": PAGE_LIMIT,
            "page": page,
        }
        logger.info("Запрос hh: query=%r, area=%d, page=%d", query, area, page)
        resp = requests.get(
            BASE_URL, params=params, headers=_headers(), timeout=REQUEST_TIMEOUT
        )
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            if resp.status_code == 403:
                logger.warning(
                    "hh отклонил запрос(403): нет токена приложения или он не активен"
                )
                raise SourceUnavailableError(
                    "hh отклонил запрос (403): нет токена приложения или он не активен"
                ) from None
            raise
        data = resp.json()
        found = data.get("found", 0)
        logger.info("hh meta: found=%s, pages=%s", found, data.get("pages"))
        batch = data.get("items") or []
        if not batch:
            logger.info("Страница %d пуста — конец выдачи", page)
            break
        for raw in batch:
            dto = normalize_hh(raw)
            if dto is not None:
                items.append(dto)
        if (page + 1) * PAGE_LIMIT >= found:
            logger.info("Конец выдачи hh: page=%d, found=%s", page, found)
            break
    logger.info("Собрано вакансий hh: %d", len(items))
    return items
