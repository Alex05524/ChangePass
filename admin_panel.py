from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QColorDialog, QFontDialog, QInputDialog, QMessageBox, QCheckBox, QStyleFactory
from PyQt5 import QtCore

class AdminPanel(QDialog):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle('Панель администратора')
        self.setFixedSize(400, 300)
        self.set_default_style()
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

        self.reset_defaults_btn = QPushButton('Сбросить настройки по умолчанию')
        self.reset_defaults_btn.clicked.connect(self.reset_to_defaults)
        layout.addWidget(self.reset_defaults_btn)

        self.close_button = QPushButton('Закрыть')
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def set_default_style(self):
        self.setStyleSheet(""" 
            QDialog {
                background-color: #2e2e2e;
                color: #ffffff;
                font-family: Arial, sans-serif;
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
        """)

    def change_background_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.main_window.setStyleSheet(f"QWidget {{ background-color: {color.name()}; }}")

    def change_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.main_window.setFont(font)

    def change_interface_size(self):
        width, ok1 = QInputDialog.getInt(self, 'Изменить размер', 'Ширина:', value=self.main_window.width(), min=100, max=1920)
        height, ok2 = QInputDialog.getInt(self, 'Изменить размер', 'Высота:', value=self.main_window.height(), min=100, max=1080)
        if ok1 and ok2:
            self.main_window.resize(width, height)

    def toggle_auto_resize(self, state):
        self.main_window.auto_resize_enabled = (state == QtCore.Qt.Checked)

    def reset_to_defaults(self):
        self.main_window.auto_resize_enabled = True
        self.auto_resize_checkbox.setChecked(True)
        self.main_window.setStyleSheet("")  # Установите стиль по умолчанию, если нужно
        QMessageBox.information(self, "Сброс", "Настройки сброшены к значениям по умолчанию.")
