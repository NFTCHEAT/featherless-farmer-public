import os
import time

import requests

CAPZY_KEY = os.environ.get("CAPZY_KEY", "")
API_BASE = "https://api.capzy.ai"


def solve_turnstile(sitekey, url, api_key=None):
    if api_key is None:
        api_key = CAPZY_KEY

    task = requests.post(f"{API_BASE}/createTask", json={
        "clientKey": api_key,
        "task": {
            "type": "AntiTurnstileTaskProxyLess",
            "websiteKey": sitekey,
            "websiteURL": url,
        },
    }, timeout=30).json()

    task_id = task.get("taskId")
    if not task_id:
        raise Exception(f"Capzy createTask failed: {task}")

    deadline = time.time() + 120
    while time.time() < deadline:
        result = requests.post(f"{API_BASE}/getTaskResult", json={
            "clientKey": api_key,
            "taskId": task_id,
        }, timeout=30).json()

        status = result.get("status")
        if status == "ready":
            return result["solution"]["token"]
        elif status == "failed":
            raise Exception(f"Capzy solve failed: {result}")

        time.sleep(1)

    raise Exception("Capzy solve timeout")
