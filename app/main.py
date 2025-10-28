# app/main.py
import sys
from pathlib import Path
import traceback

# Ensure project root is on sys.path (defensive)
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load .env early so other modules can read environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=ROOT / ".env")

from PySide6.QtWidgets import QApplication
from app.ui.login_window import LoginWindow
from app.ui.dashboard_window import DashboardWindow
from app.utils.state import AppState
from app.api.auth_client import fetch_user_profile


class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = None
        self.dashboard_window = None

    def show_login(self):
        # Close dashboard if open
        try:
            if self.dashboard_window:
                self.dashboard_window.close()
        except Exception:
            pass
        self.dashboard_window = None

        # Create and show login window
        self.login_window = LoginWindow(self.show_dashboard)
        self.login_window.show()

    def show_dashboard(self):
        # Close login window if open
        try:
            if self.login_window:
                self.login_window.close()
        except Exception:
            pass
        self.login_window = None

        # Create and show dashboard window
        self.dashboard_window = DashboardWindow(self.show_login)
        self.dashboard_window.show()

    def run(self):
        """
        App startup logic:
          - If there's an access token persisted, try to fetch profile.
            - If profile fetch succeeds, go straight to dashboard.
            - Otherwise, show login.
        """
        started = False
        try:
            token = AppState.get_access_token()
            if token:
                try:
                    prof = fetch_user_profile()
                    # fetch_user_profile returns a dict {"status":"success","profile":...} or error form
                    if prof.get("status") == "success":
                        # Normalize the profile shape to get email/id/role where possible
                        profile_data = prof.get("profile") or {}
                        user_obj = profile_data.get("user") if isinstance(profile_data, dict) else None
                        if user_obj:
                            user_id = user_obj.get("id") or user_obj.get("user_id")
                            email = user_obj.get("email") or AppState.get_user_email()
                            role = user_obj.get("role") or profile_data.get("role")
                        else:
                            user_id = profile_data.get("id") or None
                            email = profile_data.get("email") or AppState.get_user_email()
                            role = profile_data.get("role") if isinstance(profile_data, dict) else None

                        AppState.set_user(email, role, token, user_id)
                        self.show_dashboard()
                        started = True
                    else:
                        # token invalid or fetch failed -> clear persisted auth and show login
                        AppState.clear_auth()
                        AppState.clear()
                except Exception:
                    # if profile fetch throws, treat as invalid token and show login
                    AppState.clear_auth()
                    AppState.clear()
                    # fallthrough to show_login
                    traceback.print_exc()
        except Exception:
            # defensive: any error fall back to login
            traceback.print_exc()

        if not started:
            self.show_login()

        sys.exit(self.app.exec())


if __name__ == "__main__":
    controller = AppController()
    controller.run()
