"""Токен приложения hh.ru (grant_type=client_credentials).

Доступ к поиску вакансий hh даёт только токену приложения: он получается
прямым запросом по client_id/client_secret, без браузерной авторизации.
Токен короткоживущий, поэтому держим его в памяти и обновляем по мере истечения.
"""

import logging
import threading
import time

import requests

from .config import HH_CLIENT_ID, HH_CLIENT_SECRET

logger = logging.getLogger(__name__)

TOKEN_URL = "https://hh.ru/oauth/token"
_TOKEN_LIFETIME_SLACK = 60  # обновляем за минуту до истечения

_access_token = ""
_expires_at = 0.0
_lock = threading.Lock()


def is_configured() -> bool:
    """True, если в .env заданы ключи приложения hh."""
    return bool(HH_CLIENT_ID and HH_CLIENT_SECRET)


def _request_token() -> tuple[str, int]:
    """Обмен client_id/client_secret на access_token приложения."""
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": HH_CLIENT_ID,
            "client_secret": HH_CLIENT_SECRET,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"hh token вернул {resp.status_code}: {resp.text[:200]}")
    payload = resp.json()
    return payload["access_token"], int(payload.get("expires_in", 0))


def get_access_token() -> str:
    """Актуальный access_token приложения; при истечении берёт новый."""
    if not is_configured():
        return ""
    global _access_token, _expires_at
    with _lock:
        if _access_token and time.time() < _expires_at:
            return _access_token
    # Запрос токена — вне лока: параллельные сборщики не сериализуем,
    # последний записанный токен победит; все токены равноценны.
    try:
        token, expires_in = _request_token()
    except Exception:
        logger.exception("Не удалось получить токен hh (client_credentials)")
        return ""
    with _lock:
        _access_token = token
        _expires_at = time.time() + expires_in - _TOKEN_LIFETIME_SLACK
    return _access_token
