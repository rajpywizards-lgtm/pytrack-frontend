# app/api/auth_client.py
from typing import Dict, Any, Optional
from app.api._http import api_post, api_get
from app.utils.state import AppState


def login_user(email: str, password: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Attempt to log in via backend /user/login.
    On success, persists tokens in QSettings (AppState) and fetches /user/me
    to populate runtime user_id/email.

    Returns a dict with keys:
      - status: "success" or "error"
      - message: error message when status == "error"
      - user_email, user_id when success
    """
    try:
        resp = api_post("/user/login", json={"email": email, "password": password}, timeout=timeout)
        # api_post returns requests.Response
        if resp.status_code != 200:
            # try to extract server message
            try:
                body = resp.json()
                msg = body.get("detail") or body.get("message") or body.get("error") or resp.text
            except Exception:
                msg = resp.text
            return {"status": "error", "message": msg}

        data = resp.json()
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        user_email = data.get("user_email") or email

        if not access_token:
            return {"status": "error", "message": "Login succeeded but access token missing from response."}

        # persist tokens & email
        AppState.set_tokens(access_token, refresh_token, user_email)
        # runtime user fields (we'll try to fetch user_id next)
        AppState.set_user(user_email, None, access_token, None)

        # Fetch /user/me to get server-side user id and authoritative email
        me_resp = api_get("/user/me")
        if me_resp.status_code == 200:
            try:
                me = me_resp.json()
                # expected shape: {"status":"success","user":{"id": "...", "email": "..."}}
                user_obj = me.get("user") if isinstance(me, dict) else None
                if user_obj:
                    user_id = user_obj.get("id")
                    user_email_from_server = user_obj.get("email") or user_email
                    # update runtime state (role unknown here)
                    AppState.set_user(user_email_from_server, getattr(AppState, "user_role", None), access_token, user_id)
                else:
                    # fallback: maybe /user/me returns direct keys
                    if me.get("id"):
                        AppState.set_user(me.get("email", user_email), getattr(AppState, "user_role", None), access_token, me.get("id"))
            except Exception:
                # non-fatal: we already saved tokens
                pass

        return {"status": "success", "user_email": AppState.get_user_email(), "user_id": AppState.user_id}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def fetch_user_profile() -> Dict[str, Any]:
    """
    Fetch /user/me using the stored token. If token is invalid,
    AppState will be cleared by _http helper and you'll get a 401 result.
    Returns the parsed JSON from the server or a dict with status:error.
    """
    try:
        resp = api_get("/user/me")
        if resp.status_code != 200:
            try:
                return {"status": "error", "message": resp.json()}
            except Exception:
                return {"status": "error", "message": resp.text}
        return {"status": "success", "profile": resp.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def logout_user() -> None:
    """
    Clear persisted and runtime auth state. Call this on logout.
    """
    AppState.clear_auth()
    AppState.clear()
