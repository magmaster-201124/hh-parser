FROM python:3.13-slim

# Отключаем байт‑код и буферизацию
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Обновляем встроенные в образ пакеты с известными CVE
RUN pip install --no-cache-dir --upgrade pip "setuptools>=78.1.1" "urllib3>=2.8.0" "msgpack>=1.2.3"

# Сначала зависимости — слой кэшируется
COPY requirements.txt  requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Затем код
COPY app/ ./app/
COPY tests/ ./tests/

EXPOSE 8000

CMD ["uvicorn", "app.web:app", "--host", "0.0.0.0", "--port", "8000"]
