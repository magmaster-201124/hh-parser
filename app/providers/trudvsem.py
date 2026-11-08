from __future__ import annotations
import logging

import requests

from .base import VacancyDTO, parse_dt

logger = logging.getLogger(__name__)

BASE_URL = "https://opendata.trudvsem.ru/api/v1/vacancies"
HEADERS: dict[str, str] = {"User-Agent": "Resumetto-parser/1.0 (test task)"}
PAGE_LIMIT = 100
REQUEST_TIMEOUT = 60


def _first_phone(contact_list: list | None) -> str | None:
    for item in contact_list or []:
        if "телефон" in str(item.get("contact_type", "")).lower():
            return item.get("contact_value")
    return None


def normalize_vacancy(vac: dict) -> VacancyDTO | None:
    """Превращает сырой vacancy-объект trudvsem в DTO. Без id — пропускаем."""
    vac_id = str(vac.get("id") or "").strip()
    if not vac_id:
        logger.warning("Вакансия без id, пропущена")
        return None

    phone = _first_phone(vac.get("contact_list"))
    currency = vac.get("currency")

    return VacancyDTO(
        hh_id=vac_id,
        title=vac.get("job-name") or "",
        company=(vac.get("company") or {}).get("name"),
        url=vac.get("vac_url") or "",
        area=(vac.get("region") or {}).get("name"),
        salary_from=vac.get("salary_min"),
        salary_to=vac.get("salary_max"),
        currency=currency.strip("«» ") if currency else None,
        has_phone=phone is not None,
        phone=phone,
        contact_name=(vac.get("contact_person") or "").strip() or None,
        published_at=parse_dt(
            vac.get("date_modify") or vac.get("creation-date")),
        raw_json=vac,
    )


def fetch_vacancies(query: str, pages: int = 1) -> list[VacancyDTO]:
    """Собирает вакансии постранично.

    Останавливается, если: страница пуста, offset вышел за пределы
    total из meta, или API отдал 5xx не на первой странице.
    """
    items: list[VacancyDTO] = []
    total: int | None = None
    offset = 0
    for page in range(max(pages, 1)):
        offset = page * PAGE_LIMIT
        if total is not None and offset >= total:
            logger.info("Конец выдачи: offset=%d >= total=%s", offset, total)
            break
        params: dict[str, str | int] = {
            "text": query,
            "limit": PAGE_LIMIT,
            "offset": offset,
        }
        logger.info("Запрос trudvsem: query=%r, offset=%d", query, offset)
        resp = requests.get(BASE_URL, params=params, headers=HEADERS,
                            timeout=REQUEST_TIMEOUT)
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            if total is not None:
                logger.warning("API отдал %s на offset=%d — считаю пагинацию "
                               "законченной", resp.status_code, offset)
                break
            raise  # первая страница не удалась — это уже честная ошибка
        data = resp.json()
        meta = data.get("meta") or {}
        total = meta.get("total", total)
        logger.info("meta: total=%s, limit=%s", total, meta.get("limit"))
        vacancies = data.get("results", {}).get("vacancies", [])
        if not vacancies:
            logger.info("Страница %d пуста — конец выдачи", page)
            break
        for wrapper in vacancies:
            dto = normalize_vacancy(wrapper.get("vacancy") or {})
            if dto is not None:
                items.append(dto)
    logger.info("Собрано вакансий: %d", len(items))
    return items
