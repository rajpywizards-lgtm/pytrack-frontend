from api.auth_client import login_user
from utils.state import AppState
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("PyTrack - Login")
        self.setGeometry(600, 300, 400, 220)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)

        layout.addWidget(QLabel("🔐 Login to PyTrack", alignment=Qt.AlignCenter))
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "Missing Info", "Please enter both email and password.")
            return

        res = login_user(email, password)
        if not res["success"]:
            QMessageBox.critical(self, "Login Failed", res["error"])
            return

        data = res["data"]
        token = data.get("access_token")
        user = data.get("user", {})
        role = user.get("role", "employee")
        AppState.set_user(email, role, token)
        QMessageBox.information(self, "Success", f"Welcome, {email}!")
        self.on_login_success()
