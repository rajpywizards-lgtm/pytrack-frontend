import os
import requests
from dotenv import load_dotenv
from utils.state import AppState

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def get_my_tasks():
    """Fetch the current user's tasks from the backend."""
    token = AppState.token
    if not token:
        return {"success": False, "error": "No auth token found"}

    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(f"{API_BASE_URL}/task/my-tasks", headers=headers)
        if res.status_code != 200:
            return {"success": False, "error": f"{res.status_code}: {res.text}"}

        data = res.json()

        # Support multiple possible response formats
        if isinstance(data, dict):
            if "tasks" in data:
                tasks = data["tasks"]
            elif "data" in data and isinstance(data["data"], list):
                tasks = data["data"]
            else:
                tasks = []
        elif isinstance(data, list):
            tasks = data
        else:
            tasks = []

        return {"success": True, "data": tasks}

    except Exception as e:
        return {"success": False, "error": str(e)}
