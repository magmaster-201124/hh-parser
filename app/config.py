import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "parser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "parser")
DB_NAME = os.getenv("DB_NAME", "vacancies")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

HH_QUERY = os.getenv("HH_QUERY", "продакт менеджер ИИ")
TRUDVSEM_QUERY = os.getenv("TRUDVSEM_QUERY", "продакт менеджер")
HH_AREA = int(os.getenv("HH_AREA", "113"))
HH_API_TOKEN = os.getenv("HH_API_TOKEN", "")
MAX_PAGES = int(os.getenv("MAX_PAGES", "5"))
