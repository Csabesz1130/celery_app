<#
    Usage:
    1. Save this as setup.ps1
    2. Run it from PowerShell: .\setup.ps1
    3. All files/folders will be created in the current directory.
#>

# Create directories
New-Item -ItemType Directory -Name "celery_app" -Force | Out-Null

# docker-compose.yml
@"
version: '3'
services:
  redis:
    image: redis:7-alpine
    container_name: redis_broker
    ports:
      - "6379:6379"

  celery:
    build: .
    container_name: celery_worker
    command: sh -c "celery -A celery_app worker --loglevel=INFO"
    volumes:
      - .:/app
    depends_on:
      - redis

  celery_beat:
    build: .
    container_name: celery_beat
    command: sh -c "celery -A celery_app beat --loglevel=INFO"
    volumes:
      - .:/app
    depends_on:
      - redis
      - celery

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    depends_on:
      - celery
      - celery_beat

  celery_exporter:
    image: danihodovic/celery-exporter:latest
    container_name: celery_exporter
    environment:
      BROKER_URL: "redis://redis:6379/0"
      CELERY_QUEUE: "celery"
    ports:
      - "5555:5555"
    depends_on:
      - redis

  grafana:
    image: grafana/grafana-oss:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  grafana_data:
"@ | Set-Content -Path ".\docker-compose.yml"

# prometheus.yml
@"
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: 'celery_exporter'
    static_configs:
      - targets: ['celery_exporter:5555']
"@ | Set-Content -Path ".\prometheus.yml"

# Dockerfile
@"
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["celery", "-A", "celery_app", "worker", "--loglevel=INFO"]
"@ | Set-Content -Path ".\Dockerfile"

# requirements.txt
@"
celery==5.2.7
redis==4.5.3
celery[redis]==5.2.7
celery-prometheus-exporter==2.0.0
"@ | Set-Content -Path ".\requirements.txt"

# celery_app\__init__.py
New-Item -ItemType File -Path ".\celery_app\__init__.py" -Force | Out-Null

# celery_app\celeryconfig.py
@"
import os

broker_url = os.environ.get("BROKER_URL", "redis://redis:6379/0")
result_backend = broker_url

task_annotations = {
    '*': {'rate_limit': '10/s'},
}
"@ | Set-Content -Path ".\celery_app\celeryconfig.py"

# celery_app\tasks.py
@"
import random
import logging
from celery import Celery
from celery.schedules import crontab

app = Celery('celery_app')
app.config_from_object('celery_app.celeryconfig')
logger = logging.getLogger(__name__)

@app.task
def task_a():
    if random.choice([True, False]):
        logger.info('Task A succeeded')
        return 'Success A'
    else:
        logger.error('Task A failed')
        raise Exception('Random failure in Task A')

@app.task
def task_b():
    if random.random() < 0.3:
        logger.error('Task B failed')
        raise Exception('Random failure in Task B')
    logger.info('Task B succeeded')
    return 'Success B'

@app.task
def task_c():
    if random.random() < 0.2:
        logger.error('Task C failed')
        raise Exception('Random failure in Task C')
    logger.info('Task C succeeded')
    return 'Success C'

app.conf.beat_schedule = {
    'run-task-a': {
        'task': 'celery_app.tasks.task_a',
        'schedule': crontab(minute='*/1'),  # every 1 minute
    },
    'run-task-b': {
        'task': 'celery_app.tasks.task_b',
        'schedule': crontab(minute='*/2'),  # every 2 minutes
    },
    'run-task-c': {
        'task': 'celery_app.tasks.task_c',
        'schedule': crontab(minute='*/3'),  # every 3 minutes
    },
}
"@ | Set-Content -Path ".\celery_app\tasks.py"

# README.md
@"
# Celery Monitoring with Grafana & Prometheus

## Overview
This stack runs Celery with scheduled tasks and monitors them using Prometheus + Grafana.

## Setup
1. Run: \`docker-compose up -d\`
2. Access:
   - Celery logs: \`docker-compose logs -f celery\`
   - Prometheus at http://localhost:9090
   - Grafana at http://localhost:3000 (admin/admin)
   - Celery Exporter metrics at http://localhost:5555/metrics

## Features
- Three dummy tasks (task_a, task_b, task_c) randomly succeed or fail.
- Scheduled automatically via Celery Beat.
- Celery Exporter feeds metrics to Prometheus, which are visualized in Grafana.

## Customization
- Update \`celery_app/celeryconfig.py\` or \`tasks.py\` for custom behavior.
- Adjust \`prometheus.yml\` to scrape additional endpoints if needed.
- Create or import a Grafana dashboard to visualize metrics.

"@ | Set-Content -Path ".\README.md"

Write-Host "All files and folders have been created successfully."
