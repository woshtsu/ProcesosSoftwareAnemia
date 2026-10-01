FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY scripts ./scripts
RUN useradd --create-home appuser && mkdir -p /app/datos && chown appuser /app/datos
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/api/salud')"
CMD ["uvicorn", "app.main:crear_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
