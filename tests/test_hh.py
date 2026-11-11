import pytest
import requests as requests_lib

from app.providers.base import SourceUnavailableError
from app.providers.hh import fetch_hh, normalize_hh

ITEM = {
    "id": "123456789",
    "name": "Продакт-менеджер",
    "employer": {"name": "Яндекс"},
    "alternate_url": "https://hh.ru/vacancy/123456789",
    "area": {"name": "Москва"},
    "salary": {"from": 150000, "to": 250000, "currency": "RUR"},
    "contacts": {
        "name": "Иван Петров",
        "phones": [{"city": "495", "number": "123-45-67"}],
    },
    "published_at": "2026-11-01T10:00:00+0300",
}


class ForbiddenResp:
    status_code = 403

    def raise_for_status(self) -> None:
        raise requests_lib.HTTPError("403")

    def json(self) -> dict:
        return {}


def test_normalize_hh_with_phone() -> None:
    dto = normalize_hh(ITEM)
    assert dto is not None
    assert dto.hh_id == "123456789"
    assert dto.company == "Яндекс"
    assert dto.phone == "495123-45-67"
    assert dto.has_phone is True
    assert dto.contact_name == "Иван Петров"
    assert dto.salary_from == 150_000
    assert dto.published_at is not None


def test_normalize_hh_without_contacts() -> None:
    dto = normalize_hh({"id": "1", "name": "x", "alternate_url": "u"})
    assert dto is not None
    assert dto.has_phone is False
    assert dto.phone is None


def test_fetch_hh_403_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(requests_lib, "get", lambda *a, **kw: ForbiddenResp())
    with pytest.raises(SourceUnavailableError):
        fetch_hh("тест", 113, pages=1)
