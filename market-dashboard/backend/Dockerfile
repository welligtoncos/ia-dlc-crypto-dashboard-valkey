FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Mesma imagem para BFF (Uvicorn), Celery worker e beat — só o comando muda no Compose/ECS.
# Exemplos:
#   uvicorn main:app --host 0.0.0.0 --port 8000
#   celery -A celery_app worker --loglevel=info
#   celery -A celery_app beat --loglevel=info
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
