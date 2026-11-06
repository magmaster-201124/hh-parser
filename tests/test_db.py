import json
import pathlib

import pytest
from sqlalchemy import func, select

from app.db import SessionLocal
from app.init_db import init
from app.main import upsert_vacancies
from app.models import Vacancy
from app.providers.trudvsem import normalize_vacancy

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "sample_response.json"


@pytest.fixture()
def session():
    init()  # на случай, если таблиц ещё нет
    s = SessionLocal()
    s.query(Vacancy).delete()
    s.commit()
    yield s
    s.rollback()
    s.close()


def test_upsert_is_idempotent(session):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    dtos = [d for d in (normalize_vacancy(w["vacancy"])
                        for w in data["results"]["vacancies"]) if d]

    created1, updated1 = upsert_vacancies(session, dtos)
    created2, updated2 = upsert_vacancies(session, dtos)

    assert created1 == len(dtos) and updated1 == 0
    assert created2 == 0 and updated2 == len(dtos)
    assert session.scalar(
        select(func.count()).select_from(Vacancy)) == len(dtos)
