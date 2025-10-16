# main.py
import sys
from PySide6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.dashboard_window import DashboardWindow

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = None
        self.dashboard_window = None

    def show_login(self):
        self.dashboard_window = None
        self.login_window = LoginWindow(self.show_dashboard)
        self.login_window.show()

    def show_dashboard(self):
        self.login_window.close()
        self.dashboard_window = DashboardWindow(self.show_login)
        self.dashboard_window.show()

    def run(self):
        self.show_login()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = AppController()
    controller.run()
