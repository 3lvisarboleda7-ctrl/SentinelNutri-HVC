FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para Playwright Chromium y compilación ligera
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps chromium

COPY src/ ./src/
ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "sentinelnutri.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

