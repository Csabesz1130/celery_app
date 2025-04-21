# celery_app/wsgi.py
from flask import Flask
from .web import app as flask_app

if __name__ == "__main__":
    flask_app.run(host='0.0.0.0', port=5000, debug=True)