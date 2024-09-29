from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QColorDialog, QFontDialog, QInputDialog, QMessageBox, QCheckBox
from PyQt5 import QtCore

class AdminPanel(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('Панель администратора')
        self.setFixedSize(400, 300)
        self.setStyle()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel('Админ-панель для настройки интерфейса программы.')
        layout.addWidget(self.label)

        self.bg_color_btn = QPushButton('Изменить цвет фона')
        self.bg_color_btn.clicked.connect(self.change_background_color)
        layout.addWidget(self.bg_color_btn)

        self.font_btn = QPushButton('Изменить шрифт')
        self.font_btn.clicked.connect(self.change_font)
        layout.addWidget(self.font_btn)

        self.layout_size_btn = QPushButton('Изменить размер и расположение')
        self.layout_size_btn.clicked.connect(self.change_interface_size)
        layout.addWidget(self.layout_size_btn)

        self.auto_resize_checkbox = QCheckBox('Включить автоподгон размеров')
        self.auto_resize_checkbox.setChecked(self.main_window.auto_resize_enabled)
        self.auto_resize_checkbox.stateChanged.connect(self.toggle_auto_resize)
        layout.addWidget(self.auto_resize_checkbox)

        self.reset_btn = QPushButton('Сбросить настройки')
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        layout.addWidget(self.reset_btn)

        # Кнопка для сброса ранее использованных паролей
        self.reset_passwords_btn = QPushButton('Сбросить ранее использованные пароли')
        self.reset_passwords_btn.clicked.connect(self.reset_used_passwords)
        layout.addWidget(self.reset_passwords_btn)

        self.setLayout(layout)

    def change_background_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.main_window.change_background_color(color.name())

    def change_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.main_window.change_font(font)

    def change_interface_size(self):
        new_size, ok = QInputDialog.getText(self, 'Изменить размер', 'Введите новый размер окна (ширина, высота):')
        if ok and ',' in new_size:
            try:
                width, height = map(int, new_size.split(','))
                self.main_window.resize_interface(width, height)
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Неверный формат размера")

    def toggle_auto_resize(self, state):
        self.main_window.toggle_auto_resize(state == QtCore.Qt.Checked)

    def reset_to_defaults(self):
        self.main_window.reset_to_defaults()

    def reset_used_passwords(self):
        self.main_window.previous_passwords.clear()
        QMessageBox.information(self, "Успех", "Ранее использованные пароли были сброшены.")

    def setStyle(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
                color: #ffffff;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056a3;
            }
            QCheckBox {
                color: #ffffff;
            }
        """)
