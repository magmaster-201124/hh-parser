import os

from dotenv import load_dotenv

load_dotenv()

_database_url = os.getenv("DATABASE_URL")
if not _database_url:
    raise RuntimeError("DATABASE_URL не задан. Скопируй .env.example в .env")

DATABASE_URL: str = _database_url  # mypy знает: здесь уже точно str

HH_QUERY = os.getenv("HH_QUERY", "продакт менеджер ИИ")
TRUDVSEM_QUERY = os.getenv("TRUDVSEM_QUERY", "продакт менеджер")
HH_AREA = int(os.getenv("HH_AREA", "113"))
MAX_PAGES = int(os.getenv("MAX_PAGES", "5"))
