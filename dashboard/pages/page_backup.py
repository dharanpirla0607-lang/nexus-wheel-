"""
Backup and Restore Page for Nexus Wheel Dashboard.
Full JSON import/export and database restoration.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from database.db import DatabaseManager

class BackupRestorePage(QWidget):
    configuration_restored = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseManager()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Backup & Restore")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #FFFFFF;")
        layout.addWidget(title)

        desc = QLabel("Export your configured radial wheels, categories, and keybindings to JSON or restore from a file.")
        desc.setStyleSheet("color: #8B949E; margin-bottom: 8px;")
        layout.addWidget(desc)

        # 1. Export Card
        c1 = QFrame()
        c1.setObjectName("card")
        l1 = QVBoxLayout(c1)
        l1.setSpacing(10)

        h1 = QLabel("Export Configuration")
        h1.setObjectName("card_header")
        l1.addWidget(h1)

        d1 = QLabel("Save all wheels, custom actions, categories, shortcuts, and appearance settings into a single JSON profile.")
        d1.setObjectName("card_desc")
        l1.addWidget(d1)

        btn_export = QPushButton("Export to JSON File")
        btn_export.setObjectName("primary_btn")
        btn_export.setFixedWidth(200)
        btn_export.clicked.connect(self._export_backup)
        l1.addWidget(btn_export)
        layout.addWidget(c1)

        # 2. Import Card
        c2 = QFrame()
        c2.setObjectName("card")
        l2 = QVBoxLayout(c2)
        l2.setSpacing(10)

        h2 = QLabel("Import & Restore")
        h2.setObjectName("card_header")
        l2.addWidget(h2)

        d2 = QLabel("Restore your entire Nexus Wheel configuration from an existing JSON backup.")
        d2.setObjectName("card_desc")
        l2.addWidget(d2)

        btn_import = QPushButton("Import from JSON File")
        btn_import.setObjectName("secondary_btn")
        btn_import.setFixedWidth(200)
        btn_import.clicked.connect(self._import_backup)
        l2.addWidget(btn_import)
        layout.addWidget(c2)

        # 3. Factory Reset Card
        c3 = QFrame()
        c3.setObjectName("card")
        l3 = QVBoxLayout(c3)
        l3.setSpacing(10)

        h3 = QLabel("Factory Reset")
        h3.setObjectName("card_header")
        l3.addWidget(h3)

        d3 = QLabel("Wipes custom configurations and re-initializes all 5 default radial wheels (Main, Gaming, Productivity, Media, Developer).")
        d3.setObjectName("card_desc")
        l3.addWidget(d3)

        btn_reset = QPushButton("Reset All to Default")
        btn_reset.setObjectName("danger_btn")
        btn_reset.setFixedWidth(200)
        btn_reset.clicked.connect(self._factory_reset)
        l3.addWidget(btn_reset)
        layout.addWidget(c3)

        layout.addStretch()

    def _export_backup(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Configuration", "nexus_wheel_backup.json", "JSON Files (*.json)")
        if path:
            json_str = self._db.export_backup_json()
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_str)
            QMessageBox.information(self, "Success", f"Configuration successfully exported to:\n{path}")

    def _import_backup(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Configuration", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if self._db.import_backup_json(content):
                    QMessageBox.information(self, "Success", "Configuration successfully imported and applied.")
                    self.configuration_restored.emit()
                else:
                    QMessageBox.critical(self, "Error", "Failed to restore backup. Invalid JSON format.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not read file: {e}")

    def _factory_reset(self):
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to restore factory default configuration?\nThis will re-initialize all default wheels and shortcuts.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            import os
            from database.schema import DB_FILE, init_database
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            init_database()
            QMessageBox.information(self, "Success", "Factory defaults restored.")
            self.configuration_restored.emit()
