# Celery Monitoring with Grafana & Prometheus

## Overview
This stack runs Celery with scheduled tasks and monitors them using Prometheus + Grafana.

## Setup
1. Run: \docker-compose up -d\
2. Access:
   - Celery logs: \docker-compose logs -f celery\
   - Prometheus at http://localhost:9090
   - Grafana at http://localhost:3000 (admin/admin)
   - Celery Exporter metrics at http://localhost:5555/metrics

## Features
- Three dummy tasks (task_a, task_b, task_c) randomly succeed or fail.
- Scheduled automatically via Celery Beat.
- Celery Exporter feeds metrics to Prometheus, which are visualized in Grafana.

## Customization
- Update \celery_app/celeryconfig.py\ or \	asks.py\ for custom behavior.
- Adjust \prometheus.yml\ to scrape additional endpoints if needed.
- Create or import a Grafana dashboard to visualize metrics.

