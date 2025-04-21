FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add gunicorn for production-ready server
RUN pip install gunicorn

COPY . .

# Add Python unbuffered environment variable for better logging
ENV PYTHONUNBUFFERED=1
# Add Python path
ENV PYTHONPATH=/app

# Default command will be overridden by docker-compose
CMD ["python", "-m", "flask", "--app", "celery_app.web", "run", "--host=0.0.0.0", "--port=5000"]