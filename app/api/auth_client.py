import os, requests
from dotenv import load_dotenv
load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def login_user(email: str, password: str):
    """Login via FastAPI backend"""
    try:
        res = requests.post(f"{API_BASE_URL}/user/login", json={"email": email, "password": password})
        if res.status_code == 200:
            return {"success": True, "data": res.json()}
        else:
            return {"success": False, "error": res.text}
    except Exception as e:
        return {"success": False, "error": str(e)}
