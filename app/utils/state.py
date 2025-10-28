from PySide6.QtCore import QSettings
from typing import Optional


class AppState:
    """
    Centralized app state & persisted auth helpers.
    Use AppState.get_access_token(), AppState.set_tokens(...), AppState.clear_auth(), etc.
    """

    # in-memory (runtime) fields
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    token: Optional[str] = None
    user_id: Optional[str] = None

    # App/org IDs used for persistence
    _ORG = "PyTrack"
    _APP = "PyTrackDesktop"

    # QSettings instance (class-level)
    _settings = QSettings(_ORG, _APP)

    # -------------------------
    # Persistence helpers
    # -------------------------
    @staticmethod
    def set_tokens(access_token: Optional[str], refresh_token: Optional[str] = None, user_email: Optional[str] = None) -> None:
        """Persist tokens and email to QSettings (or remove if None)."""
        if access_token:
            AppState._settings.setValue("auth/access_token", access_token)
        else:
            AppState._settings.remove("auth/access_token")

        if refresh_token:
            AppState._settings.setValue("auth/refresh_token", refresh_token)
        else:
            AppState._settings.remove("auth/refresh_token")

        if user_email:
            AppState._settings.setValue("auth/user_email", user_email)
        else:
            AppState._settings.remove("auth/user_email")

        # keep runtime copy consistent
        AppState.token = access_token
        AppState.user_email = user_email

    @staticmethod
    def get_access_token() -> Optional[str]:
        val = AppState._settings.value("auth/access_token", None)
        return str(val) if val else None

    @staticmethod
    def get_refresh_token() -> Optional[str]:
        val = AppState._settings.value("auth/refresh_token", None)
        return str(val) if val else None

    @staticmethod
    def get_user_email() -> Optional[str]:
        val = AppState._settings.value("auth/user_email", None)
        return str(val) if val else None

    @staticmethod
    def clear_auth() -> None:
        """Remove persisted auth and clear runtime token/email."""
        AppState._settings.remove("auth/access_token")
        AppState._settings.remove("auth/refresh_token")
        AppState._settings.remove("auth/user_email")
        AppState.token = None
        AppState.user_email = None

    # -------------------------
    # Runtime-only helpers
    # -------------------------
    @classmethod
    def set_user(cls, email: Optional[str], role: Optional[str], token: Optional[str], user_id: Optional[str] = None) -> None:
        """
        Set runtime-only user fields. This does NOT persist tokens unless you also call set_tokens().
        """
        cls.user_email = email
        cls.user_role = role
        cls.token = token
        cls.user_id = user_id

    @classmethod
    def clear(cls) -> None:
        """Clear runtime-only state (does not touch persisted QSettings)."""
        cls.user_email = None
        cls.user_role = None
        cls.token = None
        cls.user_id = None
