from __future__ import annotations

import logging
import pathlib
import threading
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from .config import (
    HH_AREA,
    HH_QUERY,
    MAX_PAGES,
    TRUDVSEM_QUERY,
)
from .db import SessionLocal
from .main import upsert_vacancies
from .models import Vacancy
from .providers.base import SourceUnavailableError
from .providers.hh import fetch_hh
from .providers.trudvsem import fetch_vacancies

logger = logging.getLogger(__name__)

app = FastAPI(title="Resumetto", version="0.1.0")

STATIC_DIR = pathlib.Path(__file__).parent / "static"
SOURCES = ("trudvsem", "hh")

_status: dict[str, dict] = {}
_lock = threading.Lock()


class VacancyOut(BaseModel):
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
    published_at: datetime | None
    contact_name: str | None


def _set_status(source: str, **kwargs) -> None:
    with _lock:
        _status.setdefault(source, {}).update(kwargs)


def _run_collection(source: str) -> None:
    """Фоновая задача: собирает выбранный источник и пишет в БД."""
    try:
        if source == "trudvsem":
            items = fetch_vacancies(TRUDVSEM_QUERY, MAX_PAGES)
        else:
            items = fetch_hh(HH_QUERY, HH_AREA, MAX_PAGES)
        with SessionLocal() as session:
            created, updated = upsert_vacancies(session, items)
        _set_status(
            source, state="done", collected=len(items), created=created, updated=updated
        )
        logger.info(
            "Сбор %s завершён: собрано %d, новых %d, обновлено %d",
            source,
            len(items),
            created,
            updated,
        )
    except SourceUnavailableError as exc:
        logger.warning("Источник %s недоступен: %s", source, exc)
        _set_status(source, state="error", reason=str(exc))
    except Exception:
        logger.exception("Сбор %s упал", source)
        _set_status(source, state="error", reason="внутренняя ошибка")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/vacancies", response_model=list[VacancyOut])
def list_vacancies(
    has_phone: bool | None = None, limit: int = 50, offset: int = 0
) -> list[VacancyOut]:
    limit = min(max(limit, 1), 250)
    offset = max(offset, 0)
    with SessionLocal() as session:
        stmt = (
            select(Vacancy)
            .order_by(Vacancy.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if has_phone is not None:
            stmt = stmt.where(Vacancy.has_phone.is_(has_phone))
        rows = session.scalars(stmt).all()
        return [VacancyOut.model_validate(r, from_attributes=True) for r in rows]


@app.post("/api/collect/{source}")
def collect(source: str, background: BackgroundTasks) -> dict:
    if source not in SOURCES:
        raise HTTPException(status_code=400, detail="Неизвестный источник")
    if _status.get(source, {}).get("state") == "running":
        raise HTTPException(status_code=409, detail="Сбор уже выполняется")
    _set_status(source, state="running", started_at=datetime.now().isoformat())
    background.add_task(_run_collection, source)
    return {"detail": f"Сбор {source} запущен"}


@app.get("/api/status")
def status() -> dict:
    with _lock:
        return dict(_status)


@app.get("/health")
def health() -> dict[str, str]:
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="db unavailable")
