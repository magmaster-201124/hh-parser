import json

with open("sample_response.json", encoding="utf-8") as f:
    data = json.load(f)

vacancies = [item["vacancy"] for item in data["results"]["vacancies"]]
print(f"Всего вакансий: {len(vacancies)}")

with_phone = 0
for v in vacancies:
    contacts = v.get("contact_list") or []
    phones = [
        c["contact_value"] for c in contacts if c.get("contact_type") == "Телефон"
    ]
    if phones:
        with_phone += 1
        print(f"  {v['job-name'][:40]:40} | {phones[0]}")

print(
    f"\nС телефоном: {with_phone} из {len(vacancies)} ({100 * with_phone / len(vacancies):.0f}%)"
)

# Заодно смотрим, как выглядят зарплаты и даты — пригодится нормализации
sample = vacancies[0]
print(
    "\nsalary_min:",
    sample.get("salary_min"),
    "| salary_max:",
    sample.get("salary_max"),
    "| currency:",
    sample.get("currency"),
)
print("creation-date:", sample.get("creation-date"))
print("region:", sample.get("region"))
print("addresses:", sample.get("addresses"))
