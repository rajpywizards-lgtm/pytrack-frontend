# app/ui/login_window.py
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QVBoxLayout, QFrame, QMessageBox, QApplication
)
from PySide6.QtGui import QPixmap, QGuiApplication
from PySide6.QtCore import Qt
import os

# use our frontend clients and state
from app.api.auth_client import login_user, fetch_user_profile
from app.utils.state import AppState


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("PyTrack - Login")

        # ----------- SCREEN CENTERING LOGIC -----------
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * 0.53)
        height = int(screen.height() * 0.53)
        x = int((screen.width() - width) / 2)
        y = int((screen.height() - height) / 2)
        self.setGeometry(x, y, width, height)

        # Load QSS safely (fall back if file missing)
        qss_path = os.path.join(os.path.dirname(__file__), "..", "styles", "login.qss")
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception:
            # ignore styling errors, app still works
            pass

        # ---------------- MAIN LAYOUT ----------------
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------- LEFT PANEL ----------------
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")

        # Center everything in both directions
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignCenter)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # --- App Logo ---
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "company_logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(174, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setObjectName("AppLogo")
            left_layout.addWidget(logo_label)

        # --- Form elements ---
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Company Email")
        self.email_input.setFixedWidth(280)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(280)

        self.login_btn = QPushButton("Login")
        self.forgot_btn = QPushButton("Forgot your password?")
        self.forgot_btn.setObjectName("ForgotButton")

        self.login_btn.clicked.connect(self.handle_login)

        for w in [self.email_input, self.password_input, self.login_btn, self.forgot_btn]:
            w.setMaximumWidth(300)
            left_layout.addWidget(w, alignment=Qt.AlignCenter)

        # ---------------- RIGHT PANEL ----------------
        right_panel = QFrame()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        bg_path = os.path.join(os.path.dirname(__file__), "assets", "bg.png")
        if os.path.exists(bg_path):
            bg_label = QLabel()
            pixmap = QPixmap(bg_path)
            # Fit vertically, allow cropping by KeepAspectRatioByExpanding
            bg_label.setPixmap(
                pixmap.scaled(300, int(screen.height() * 0.53), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            )
            bg_label.setAlignment(Qt.AlignCenter)
            right_layout.addWidget(bg_label)

        # ---------------- COMBINE ----------------
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
        self.setLayout(main_layout)

    # ---------------- LOGIN HANDLER ----------------
    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Missing Info", "Please enter your email and password.")
            return

        # disable UI while we attempt login
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Logging in...")

        try:
            QGuiApplication.setOverrideCursor(Qt.WaitCursor)
            # login_user persists tokens into AppState and returns structured result
            res = login_user(email, password)
            QGuiApplication.restoreOverrideCursor()

            if res.get("status") != "success":
                # show server-provided error when available
                msg = res.get("message") or "Invalid email or password."
                QMessageBox.critical(self, "Login Failed", str(msg))
                return

            # At this point AppState has tokens saved already by login_user.
            # Fetch profile to obtain authoritative user id (and possibly role)
            prof = fetch_user_profile()
            if prof.get("status") != "success":
                # profile fetch failed; still proceed but warn user
                # clear auth to be safe
                AppState.clear_auth()
                AppState.clear()
                QMessageBox.critical(self, "Error", "Failed to fetch user profile after login.")
                return

            # profile payload expected: {"status":"success","profile": {"user": {...}} } or {"status":"success","profile": {...}}
            profile_data = prof.get("profile") or {}
            user_obj = profile_data.get("user") if isinstance(profile_data, dict) else None

            # Normalize user_id/email
            if user_obj:
                user_id = user_obj.get("id") or user_obj.get("user_id")
                user_email = user_obj.get("email") or AppState.get_user_email()
            else:
                # fallback if profile returned direct keys or different shape
                user_id = profile_data.get("id") or None
                user_email = profile_data.get("email") or AppState.get_user_email()

            # Set runtime user fields (role unknown from this endpoint unless returned)
            role = profile_data.get("role") if isinstance(profile_data, dict) else None
            AppState.set_user(user_email, role, AppState.get_access_token(), user_id)

            # Call callback to transition to main app
            try:
                self.on_login_success()
            except Exception:
                # swallow UI callback errors but inform user
                QMessageBox.information(self, "Logged In", "Login successful, but could not open dashboard.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            QGuiApplication.restoreOverrideCursor()
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Login")
