from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QVBoxLayout, QFrame, QMessageBox, QApplication
)
from PySide6.QtGui import QPixmap, QGuiApplication
from PySide6.QtCore import Qt
import os
from api.auth_client import login_user
from utils.state import AppState


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

        # Load QSS
        qss_path = os.path.join(os.path.dirname(__file__), "..", "styles", "login.qss")
        with open(qss_path, "r") as f:
            self.setStyleSheet(f.read())

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
        self.email_input.setFixedWidth(280)  # widen input field

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

        # Disable login button during request
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Logging in...")

        try:
            QGuiApplication.setOverrideCursor(Qt.WaitCursor)
            res = login_user(email, password)
            if not res["success"]:
                QMessageBox.critical(self, "Login Failed", res["error"])
                self.login_btn.setEnabled(True)
                self.login_btn.setText("Login")
                return
            QGuiApplication.restoreOverrideCursor()

            data = res["data"]
            token = data.get("access_token")
            user = data.get("user", {})
            role = user.get("role", "employee")

            if not token:
                QMessageBox.critical(self, "Error", "No token received from server.")
                self.login_btn.setEnabled(True)
                self.login_btn.setText("Login")
                return

            # Save user data to global state
            AppState.set_user(email, role, token)

            # 🟢 Go straight to dashboard (no confirmation popup)
            self.on_login_success()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

        finally:
            # Always reset button state
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Login")

