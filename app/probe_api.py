import json
import requests

from .config import HH_QUERY, HH_AREA

BASE_URL = "https://api.hh.ru/vacancies"
HEADERS: dict[str, str] = {
    "User-Agent": "Resumetto-parser/1.0 (test task)"}
params: dict[str, str] = {
    "text": HH_QUERY,
    "area": str(HH_AREA),
    "per_page": "20",
    "page": "0",
}


def probe() -> None:

    resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
    print("HTTP", resp.status_code)
    print(resp.text[:1000])
    if resp.status_code != 200:
        resp.raise_for_status()
    payload = resp.json()

    # верхний уровень ответа
    print("Ключи верхнего уровня:", list(payload.keys()))
    print(f"Всего найдено: {payload.get('found')}, "
          f"страниц: {payload.get('pages')}"
          )

    # структура одной вакансии
    item = payload["items"][0]
    print("Ключи вакансии:", sorted(item.keys()))

    # сохраняем сырой ответ для изучения
    with open("sample_response.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("Сырой ответ сохранён в sample_response.json")


if __name__ == "__main__":
    probe()
