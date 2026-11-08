import json
import pathlib

from app.providers.base import parse_dt
from app.providers.trudvsem import fetch_vacancies, normalize_vacancy

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "sample_response.json"


def _vacancies() -> list[dict]:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return [w["vacancy"] for w in data["results"]["vacancies"]]


def test_normalize_main_fields() -> None:
    vac = _vacancies()[0]
    dto = normalize_vacancy(vac)
    assert dto is not None
    assert dto.hh_id == "b7d2712e-73f1-11f0-b34a-e7d0d2cf29b1"
    assert dto.title == "Продакт-менеджер"
    assert dto.company == 'ООО "ДНС РИТЕЙЛ"'
    assert dto.area == "Приморский край"
    assert dto.salary_from == 91_954
    assert dto.salary_to == 91_954
    assert dto.currency == "руб."
    assert dto.url.startswith("https://trudvsem.ru/vacancy/card/")


def test_has_phone_from_contact_list() -> None:
    dto = normalize_vacancy(_vacancies()[0])
    assert dto is not None
    assert dto.has_phone is True
    assert dto.phone == "+7(423) 261-46-41"
    assert dto.contact_name == "Дмитренко Александра"


def test_no_contacts_means_no_phone() -> None:
    dto = normalize_vacancy({"id": "x", "job-name": "t", "vac_url": "u"})
    assert dto is not None
    assert dto.has_phone is False
    assert dto.phone is None
    assert dto.contact_name is None


def test_missing_id_skipped() -> None:
    assert normalize_vacancy({}) is None


def test_date_parsing() -> None:
    dt1 = parse_dt("2026-11-03T07:13:04+0300")
    assert dt1 is not None
    assert dt1.isoformat() == "2026-11-03T07:13:04+03:00"

    dt2 = parse_dt("2025-08-08")  # assert dt2 is not None,не нужен для tzinfo
    assert dt2 is not None and dt2.tzinfo is not None

    assert parse_dt(None) is None
    assert parse_dt("мусор") is None


def test_fetch_stops_after_total(monkeypatch):
    """Один ответ с total=2, limit=100 — второй запрос не выполняется."""
    calls = []

    def fake_get(url, params=None, headers=None, timeout=None):
        calls.append(params)

        class R:
            status_code = 200
            def raise_for_status(self): pass

            def json(self):
                return {"meta": {"total": 2, "limit": 100},
                        "results": {"vacancies": [
                            {"vacancy": {"id": "a",
                                         "job-name": "x",
                                         "vac_url": "u"}},
                            {"vacancy": {"id": "b",
                                         "job-name": "y",
                                         "vac_url": "u"}},
                        ]}}
        return R()

    monkeypatch.setattr("app.providers.trudvsem.requests.get", fake_get)
    dtos = fetch_vacancies("тест", pages=5)
    assert len(dtos) == 2
    assert len(calls) == 1  # вторая страница не запрашивалась
