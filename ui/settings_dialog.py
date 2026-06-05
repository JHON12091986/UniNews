from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from app_settings import load_app_settings, save_app_settings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("UniNews Settings")
        self.resize(420, 300)

        self.settings = load_app_settings()

        self.setup_ui()
        self.load_values()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        form_layout = QFormLayout()

        self.refresh_on_startup_checkbox = QCheckBox("Refresh news when app starts")

        self.refresh_interval_combo = QComboBox()
        self.refresh_interval_combo.addItem("Manual only", 0)
        self.refresh_interval_combo.addItem("Every 15 minutes", 15)
        self.refresh_interval_combo.addItem("Every 30 minutes", 30)
        self.refresh_interval_combo.addItem("Every 1 hour", 60)

        self.notifications_checkbox = QCheckBox("Enable desktop notifications")

        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("deadline, scholarship, exam")

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Light", "light")
        self.theme_combo.addItem("Dark", "dark")

        self.max_cache_spinbox = QSpinBox()
        self.max_cache_spinbox.setMinimum(50)
        self.max_cache_spinbox.setMaximum(5000)
        self.max_cache_spinbox.setSingleStep(50)

        form_layout.addRow("", self.refresh_on_startup_checkbox)
        form_layout.addRow("Refresh interval:", self.refresh_interval_combo)
        form_layout.addRow("", self.notifications_checkbox)
        form_layout.addRow("Notification keywords:", self.keywords_input)
        form_layout.addRow("Theme:", self.theme_combo)
        form_layout.addRow("Max cached articles:", self.max_cache_spinbox)

        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("SaveButton")
        self.save_button.clicked.connect(self.save_settings)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)

        main_layout.addWidget(title)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

    def load_values(self):
        self.refresh_on_startup_checkbox.setChecked(
            self.settings.get("refresh_on_startup", True)
        )

        refresh_interval = self.settings.get("refresh_interval_minutes", 0)
        index = self.refresh_interval_combo.findData(refresh_interval)

        if index >= 0:
            self.refresh_interval_combo.setCurrentIndex(index)

        self.notifications_checkbox.setChecked(
            self.settings.get("notifications_enabled", False)
        )

        keywords = self.settings.get("notification_keywords", [])
        self.keywords_input.setText(", ".join(keywords))

        theme = self.settings.get("theme", "light")
        theme_index = self.theme_combo.findData(theme)

        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)

        self.max_cache_spinbox.setValue(
            self.settings.get("max_cached_articles", 500)
        )

    def save_settings(self):
        keywords_text = self.keywords_input.text().strip()

        keywords = [
            keyword.strip()
            for keyword in keywords_text.split(",")
            if keyword.strip()
        ]

        self.settings["refresh_on_startup"] = (
            self.refresh_on_startup_checkbox.isChecked()
        )
        self.settings["refresh_interval_minutes"] = (
            self.refresh_interval_combo.currentData()
        )
        self.settings["notifications_enabled"] = (
            self.notifications_checkbox.isChecked()
        )
        self.settings["notification_keywords"] = keywords
        self.settings["theme"] = self.theme_combo.currentData()
        self.settings["max_cached_articles"] = self.max_cache_spinbox.value()

        save_app_settings(self.settings)
        self.accept()