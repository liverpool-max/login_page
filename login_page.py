import sys
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Qt


def load_users_from_file(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file: {e}")
        return []


class LoginPage(QWidget):
    def __init__(self, users, switch_to_profile_callback):
        super().__init__()

        self.users = users
        self.switch_to_profile_callback = switch_to_profile_callback
        
        self.layout = QVBoxLayout()

        # Username
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.textChanged.connect(self.check_input_validity)
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)

        # Password
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)  # Şifrə gizlətmə
        self.password_input.textChanged.connect(self.check_input_validity)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        # Login as Admin Checkbox
        self.admin_checkbox = QCheckBox("Login as Admin")
        self.layout.addWidget(self.admin_checkbox)

        # Login Button
        self.login_button = QPushButton("Login")
        self.login_button.setEnabled(False)  # İlk öncə deaktivdir
        self.login_button.clicked.connect(self.login_action)
        self.layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        # Layout
        self.setLayout(self.layout)

    def check_input_validity(self):
        # Username və Password uzunluğunu yoxlayırıq
        username_valid = len(self.username_input.text()) >= 5
        password_valid = len(self.password_input.text()) >= 5

        # Login düyməsini aktivləşdiririk
        self.login_button.setEnabled(username_valid and password_valid)

    def login_action(self):
        username = self.username_input.text()
        password = self.password_input.text()
        is_admin = self.admin_checkbox.isChecked()

        # İstifadəçi məlumatları ilə yoxlama
        for user in self.users:
            if user["username"] == username and user["password"] == password:
                if is_admin and user["role"] != "admin":
                    # Pop-up mesajı göstəririk, səhv mesajı artıq etiketdə göstərilmir
                    QMessageBox.warning(self, "Login Failed", "Siz admin deyilsiniz, istifadəçi kimi girmək istəyirsinizsə login as admin butonunu söndürün")
                elif not is_admin and user["role"] == "admin":
                    # Pop-up mesajı göstəririk, səhv mesajı artıq etiketdə göstərilmir
                    QMessageBox.warning(self, "Login Failed", "Admin kimi girmək istəyirsinizsə login as admin butonunu yandırmalısınız")
                else:
                    # Uğurlu giriş zamanı səhv mesajı yoxdur
                    self.switch_to_profile_callback(user)
                return

        # Giriş səhv olduqda pop-up mesajı göstəririk
        QMessageBox.critical(self, "Login Failed", "Ad və ya parol səhvdir!!!")


class ProfilePage(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        # Məlumat etiketləri
        self.info_label = QLabel("Profilinizə xoş gəlmisiniz")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        self.username_label = QLabel("Username: ")
        self.layout.addWidget(self.username_label)

        self.role_label = QLabel("Role: ")
        self.layout.addWidget(self.role_label)

        # Logout düyməsi
        self.back_button = QPushButton("Logout")
        self.layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        # Layout
        self.setLayout(self.layout)

    def set_user_data(self, user):
        self.username_label.setText(f"Username: {user['username']}")
        self.role_label.setText(f"Role: {user['role']}")


class MainApp(QStackedWidget):
    def __init__(self, users):
        super().__init__()

        # Səhifələri yaratmaq
        self.login_page = LoginPage(users, self.switch_to_profile)
        self.profile_page = ProfilePage()

        # Səhifələri əlavə etmək
        self.addWidget(self.login_page)
        self.addWidget(self.profile_page)

        # Logout düyməsinə bağlamaq
        self.profile_page.back_button.clicked.connect(self.switch_to_login)

    def switch_to_profile(self, user):
        self.profile_page.set_user_data(user)
        self.setCurrentWidget(self.profile_page)

    def switch_to_login(self):
        self.setCurrentWidget(self.login_page)


if __name__ == "__main__":
    # JSON faylını yükləmək
    users = load_users_from_file("data.json")

    # Əgər istifadəçi məlumatları yoxdursa, proqramı dayandırmaq
    if not users:
        print("No user data found. Exiting.")
        sys.exit(1)

    app = QApplication(sys.argv)
    main_app = MainApp(users)
    main_app.setWindowTitle("Login System with External JSON Database")
    main_app.resize(400, 300)
    main_app.show()
    sys.exit(app.exec())
