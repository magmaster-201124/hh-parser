from .db import Base, engine
from . import models  # noqa: F401 — импорт регистрирует модели


def init() -> None:
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init()
    print("Таблицы созданы")
