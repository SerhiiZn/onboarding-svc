FROM python:3.11-slim

WORKDIR /app

# Копіюємо залежності та встановлюємо їх
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код додатка
COPY app/ ./app

# Створюємо директорію для артефактів та надаємо права для OpenShift (GID 0)
RUN mkdir -p /app/shared-artifacts && chmod -R g+w /app/shared-artifacts

ENV ARTIFACTS_DIR=/app/shared-artifacts
EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
