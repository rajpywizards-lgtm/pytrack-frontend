"""
Shared HTTP helpers for the frontend.

Usage:
    from app.api._http import api_get, api_post, API_URL

    resp = api_post("/user/login", json={...})
    resp.raise_for_status()
    data = resp.json()
"""
import os
import requests
from typing import Dict, Optional, Any
from requests import Response

from app.utils.state import AppState

# Base URL for backend API (adjust if needed)
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
DEFAULT_TIMEOUT = 20  # seconds


def get_auth_headers(token: Optional[str] = None) -> Dict[str, str]:
    """Return Authorization header if token exists (prefers explicit token)."""
    tok = token or AppState.get_access_token()
    return {"Authorization": f"Bearer {tok}"} if tok else {}


def _handle_401_and_return(resp: Response) -> Response:
    """
    If backend returns 401, clear stored auth so the UI can show login.
    Returns the same Response for further processing by caller.
    """
    if resp.status_code == 401:
        # Clear persisted tokens and runtime state
        AppState.clear_auth()
        AppState.clear()
    return resp


def api_get(path: str, *, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, timeout: int = DEFAULT_TIMEOUT) -> Response:
    """
    Perform GET to API_URL + path.
    `path` should start with '/' (e.g. '/user/me').
    Returns requests.Response.
    """
    url = f"{API_URL}{path}"
    h = {}
    if headers:
        h.update(headers)
    h.update(get_auth_headers())
    resp = requests.get(url, headers=h, params=params, timeout=timeout)
    return _handle_401_and_return(resp)


def api_post(path: str, *, json: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: int = DEFAULT_TIMEOUT) -> Response:
    """
    Perform POST to API_URL + path.
    Prefer sending `json=` for JSON bodies or `files=` for multipart uploads.
    Returns requests.Response.
    """
    url = f"{API_URL}{path}"
    h = {}
    if headers:
        h.update(headers)
    h.update(get_auth_headers())

    # requests will choose appropriate content-type when files is set
    resp = requests.post(url, json=json, data=data, files=files, headers=h, timeout=timeout)
    return _handle_401_and_return(resp)
