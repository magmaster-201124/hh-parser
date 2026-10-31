FROM python:3.13-slim

WORKDIR /app

# Обновляем встроенные в образ пакеты с известными CVE
RUN pip install --no-cache-dir --upgrade pip "setuptools>=78.1.1" "urllib3>=2.8.0" "msgpack>=1.2.3"

# Сначала зависимости — слой кэшируется
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем код
COPY app/ ./app/

CMD ["python", "-m", "app.main"]
