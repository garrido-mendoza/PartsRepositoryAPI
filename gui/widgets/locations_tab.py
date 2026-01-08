from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from gui.api_client import ApiClient
from gui.common.dialogs import confirm


class LocationsTab(QWidget):
    def __init__(self, client: ApiClient):
        super().__init__()
        self.client = client

        layout = QVBoxLayout(self)

        # Controls (horizontal layout)
        ctl = QHBoxLayout()
        self.location_name = QLineEdit()
        self.location_name.setPlaceholderText("Location Name")
        self.description = QLineEdit()
        self.description.setPlaceholderText("Description")
        btn_add = QPushButton("Add Location")
        btn_search = QPushButton("Search Location")
        btn_delete = QPushButton("Delete Selected")
        btn_show = QPushButton("Show Locations")
        ctl.addWidget(self.location_name)
        ctl.addWidget(self.description)
        ctl.addWidget(btn_add)
        ctl.addWidget(btn_search)
        ctl.addWidget(btn_delete)
        ctl.addWidget(btn_show)
        layout.addLayout(ctl)

        # Table (only 2 visible columns: Name + Description)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Location Name", "Description"])
        layout.addWidget(self.table)

        # Events
        btn_add.clicked.connect(self.add_location)
        btn_search.clicked.connect(self.search_location)
        btn_delete.clicked.connect(self.delete_location)
        btn_show.clicked.connect(self.show_locations)

        # Initial refresh to show all locations
        self.refresh_table()

    def refresh_table(self):
        """Refresh the table with all locations from backend using /locations/all."""
        data = self.client.list_locations()
        rows = []
        if isinstance(data, list):
            for loc in data:
                if isinstance(loc, dict) and "location_name" in loc and "description" in loc:
                    rows.append([loc["location_name"], loc["description"]])
        elif isinstance(data, dict) and "location_name" in data and "description" in data:
            rows.append([data["location_name"], data["description"]])

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_location(self):
        name = self.location_name.text().strip()
        description = self.description.text().strip()
        if not name or not description:
            QMessageBox.information(self, "Add Location", "Both name and description are required.")
            return
        result = self.client.add_location(name, description)
        if isinstance(result, dict) and ("error" in result or "message" in result):
            msg = result.get("error") or result.get("message") or "Unknown response from server."
            QMessageBox.information(self, "Add Location", str(msg))
        # Refresh full table after add
        self.refresh_table()

    def search_location(self):
        name = self.location_name.text().strip()
        if not name:
            return
        d = self.client.search_location(name)
        self.table.setRowCount(0)
        if isinstance(d, dict) and all(k in d for k in ("location_id", "location_name", "description")):
            self.table.insertRow(0)
            name_item = QTableWidgetItem(d["location_name"])
            desc_item = QTableWidgetItem(d["description"])
            name_item.setData(32, d["location_id"])  # 32 = Qt.UserRole
            self.table.setItem(0, 0, name_item)
            self.table.setItem(0, 1, desc_item)
        else:
            QMessageBox.information(
                self,
                "Search Location",
                "Location not found. Please add it first in the Locations tab."
            )

    def delete_location(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        item = self.table.item(selected, 0)
        if item is None:
            return
        location_id = item.data(32)  # retrieve hidden ID
        if not confirm("Delete Location", f"Delete location ID {location_id}?"):
            return
        self.client.delete_location(location_id)
        self.table.removeRow(selected)

    def show_locations(self):
        result = self.client.get("/locations/print")
        QMessageBox.information(self, "Show Locations", result.get("message", "Done"))
