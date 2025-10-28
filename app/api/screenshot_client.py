# app/api/screenshot_client.py
from typing import Optional, Dict, Any
from app.api._http import api_post
from datetime import datetime, timezone

def upload_screenshot(image_bytes: bytes, captured_at_iso: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
    """
    Upload an image (bytes) to the backend.
    Returns {"status": "success", "image_url": "...", "record": {...}} on success,
    or {"status": "error", "message": "..."} on failure.
    """
    try:
        files = {"image": ("screenshot.png", image_bytes, "image/png")}
        data = {}
        if captured_at_iso:
            data["captured_at"] = captured_at_iso
        else:
            # include a sensible default if caller didn't provide one
            data["captured_at"] = datetime.now(timezone.utc).isoformat()

        resp = api_post("/screenshots/upload", data=data, files=files, timeout=timeout)
        if resp.status_code in (200, 201):
            try:
                return {"status": "success", **resp.json()}
            except Exception:
                return {"status": "success", "message": "Upload succeeded but response parse failed", "raw": resp.text}
        else:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            return {"status": "error", "message": body}
    except Exception as e:
        return {"status": "error", "message": str(e)}
