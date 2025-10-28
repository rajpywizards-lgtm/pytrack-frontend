# app/api/task_client.py
from typing import Dict, Any
from app.api._http import api_get
from app.utils.state import AppState

DEFAULT_TIMEOUT = 10


def get_my_tasks(timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Fetch tasks assigned to the currently logged-in user.
    Returns a normalized dict:
      { "success": bool, "data": [...], "error": "message" }
    """
    try:
        resp = api_get("/task/my-tasks", timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            return {"success": True, "data": data.get("tasks", []), "count": data.get("count", 0)}
        # if api_get cleared auth on 401, AppState will be reset — surface that to UI
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        return {"success": False, "error": body}
    except Exception as e:
        return {"success": False, "error": str(e)}
