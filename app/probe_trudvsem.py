import json

import requests

BASE_URL = "https://opendata.trudvsem.ru/api/v1/vacancies"
HEADERS: dict[str, str] = {"User-Agent": "Resumetto-parser/1.0 (test task)"}


def probe() -> None:
    params: dict[str, str] = {"text": "продакт менеджер", "limit": "10", "offset": "0"}
    resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=60)
    print("HTTP", resp.status_code)
    resp.raise_for_status()
    data = resp.json()

    print("Ключи верхнего уровня:", list(data.keys()))
    results = data.get("results", {})
    vacancies = results.get("vacancies", [])
    print(f"Вакансий на странице: {len(vacancies)}")

    if vacancies:
        vac = vacancies[0].get("vacancy", {})
        print("Ключи vacancy:", list(vac.keys()))
        for key, value in vac.items():
            if any(word in key.lower() for word in ("contact", "phone", "tel")):
                print(f"  {key}: {value}")

    with open("sample_response.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Сырой ответ сохранён в sample_response.json")


if __name__ == "__main__":
    probe()
