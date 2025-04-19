import os

broker_url = os.environ.get("BROKER_URL", "redis://redis:6379/0")
result_backend = broker_url

task_annotations = {
    '*': {'rate_limit': '10/s'},
}
