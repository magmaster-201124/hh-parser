from . import models  # noqa: F401 — импорт регистрирует модели
from .db import Base, engine


def init() -> None:
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init()
    print("Таблицы созданы")
