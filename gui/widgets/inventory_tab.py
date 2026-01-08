from typing import Any, List, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QMessageBox, QComboBox
)
from gui.common.tables import fill_table
from gui.common.dialogs import confirm


class InventoryTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        layout = QVBoxLayout(self)

        # Controls (horizontal layout to match other tabs)
        ctl = QHBoxLayout()
        self.box_id = QLineEdit(); self.box_id.setPlaceholderText("Box ID")
        self.part_number = QLineEdit(); self.part_number.setPlaceholderText("Part Number")
        self.description = QLineEdit(); self.description.setPlaceholderText("Description")
        self.quantity = QLineEdit(); self.quantity.setPlaceholderText("Quantity")

        # Location dropdown instead of free text
        self.location_dropdown = QComboBox()
        self.location_dropdown.setPlaceholderText("Choose Location")
        self.refresh_locations()  # populate dropdown at startup

        btn_add = QPushButton("Add Inventory")
        btn_search = QPushButton("Search Inventory")
        btn_delete = QPushButton("Delete Selected")
        btn_clear = QPushButton("Clear")
        btn_call = QPushButton("Call Inventory")
        btn_update = QPushButton("Update Inventory")

        ctl.addWidget(self.location_dropdown)
        ctl.addWidget(self.box_id)
        ctl.addWidget(self.part_number)
        ctl.addWidget(self.description)
        ctl.addWidget(self.quantity)
        ctl.addWidget(btn_add)
        ctl.addWidget(btn_search)
        ctl.addWidget(btn_delete)
        ctl.addWidget(btn_clear)
        ctl.addWidget(btn_call)
        ctl.addWidget(btn_update)
        layout.addLayout(ctl)

        # Table (operator-friendly: Box ID, Part Number, Description, Location Name, Quantity)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Box ID", "Part Number", "Description", "Location Name", "Quantity"])
        layout.addWidget(self.table)

        # Internal map to track inventory IDs per displayed row
        self.id_map: List[int] = []

        # Events
        btn_add.clicked.connect(self.add_inventory)
        btn_search.clicked.connect(self.search_inventory)
        btn_delete.clicked.connect(self.delete_selected)
        btn_clear.clicked.connect(self.clear_fields)
        btn_call.clicked.connect(self.call_inventory)
        btn_update.clicked.connect(self.update_inventory)

    def refresh_locations(self):
        """Populate the location dropdown from backend using /locations/all."""
        data = self.client.list_locations()
        self.location_dropdown.clear()
        if isinstance(data, list):
            for loc in data:
                if isinstance(loc, dict) and "location_name" in loc:
                    self.location_dropdown.addItem(loc["location_name"])
        elif isinstance(data, dict) and "location_name" in data:
            self.location_dropdown.addItem(data["location_name"])

    def add_inventory(self):
        box_id = self.box_id.text().strip()
        part_number = self.part_number.text().strip()
        description = self.description.text().strip()
        location_name = self.location_dropdown.currentText().strip()
        qty = self.quantity.text().strip()
        if not box_id or not part_number or not location_name or not qty:
            return
        try:
            q_int = int(qty)
        except ValueError:
            QMessageBox.information(self, "Add Inventory", "Quantity must be an integer.")
            return
        result = self.client.add_inventory(box_id, part_number, location_name, q_int)
        if isinstance(result, dict) and ("error" in result or "message" in result):
            msg = self._normalize_msg(result.get("error"), result.get("message"))
            QMessageBox.information(self, "Add Inventory", msg)
        self.search_inventory()

    def search_inventory(self):
        box_id = self.box_id.text().strip()
        pn = self.part_number.text().strip()

        if box_id:
            data: Any = self.client.search_inventory_by_box(box_id)
        elif pn:
            data: Any = self.client.search_inventory(pn)
        else:
            return

        rows: List[List[Any]] = []
        id_map: List[int] = []

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and all(k in item for k in ("inventory_id", "box_id", "part_number", "location_name", "quantity")):
                    rows.append([item["box_id"], item["part_number"], item.get("description", ""), item["location_name"], item["quantity"]])
                    id_map.append(int(item.get("inventory_id", -1)))
        elif isinstance(data, dict):
            if all(k in data for k in ("inventory_id", "box_id", "part_number", "location_name", "quantity")):
                rows.append([data["box_id"], data["part_number"], data.get("description", ""), data["location_name"], data["quantity"]])
                id_map.append(int(data.get("inventory_id", -1)))
            elif "error" in data or "message" in data:
                msg = self._normalize_msg(data.get("error"), data.get("message"))
                QMessageBox.information(self, "Inventory Search", msg)

        fill_table(self.table, rows)
        self.id_map = id_map

    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.id_map):
            return
        inv_id = self.id_map[row]
        if inv_id is None or inv_id == -1:
            QMessageBox.information(self, "Delete Inventory", "Cannot delete: invalid inventory ID.")
            return
        if not confirm("Delete Inventory", f"Delete inventory ID {inv_id}?"):
            return
        self.client.delete_inventory(inv_id)
        self.table.removeRow(row)
        del self.id_map[row]

    def clear_fields(self):
        self.box_id.clear()
        self.part_number.clear()
        self.description.clear()
        self.quantity.clear()
        self.location_dropdown.setCurrentIndex(-1)

    def call_inventory(self):
        location_name = self.location_dropdown.currentText().strip()
        box_code = self.box_id.text().strip()
        if not location_name or not box_code:
            QMessageBox.information(self, "Call Inventory", "Location and Box ID are required.")
            return
        data = self.client.call_inventory(location_name, box_code)
        if isinstance(data, dict) and ("error" in data or "message" in data):
            msg = self._normalize_msg(data.get("error"), data.get("message"))
            QMessageBox.information(self, "Call Inventory", msg)
            return

        rows: List[List[Any]] = []
        id_map: List[int] = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and all(k in item for k in ("inventory_id", "part_number", "description", "quantity")):
                    rows.append([box_code, item["part_number"], item["description"], location_name, item["quantity"]])
                    id_map.append(int(item.get("inventory_id", -1)))
        fill_table(self.table, rows)
        self.id_map = id_map

    def update_inventory(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.id_map):
            QMessageBox.information(self, "Update Inventory", "Select a row to update.")
            return
        inv_id = self.id_map[row]
        if inv_id is None or inv_id == -1:
            QMessageBox.information(self, "Update Inventory", "Invalid inventory ID.")
            return

        part_number = self.part_number.text().strip()
        description = self.description.text().strip()
        qty = self.quantity.text().strip()
        try:
            q_int = int(qty)
        except ValueError:
            QMessageBox.information(self, "Update Inventory", "Quantity must be an integer.")
            return

        result = self.client.update_inventory(inv_id, part_number, description, q_int)
        msg = self._normalize_msg(result.get("error"), result.get("message"))
        QMessageBox.information(self, "Update Inventory", msg)
        self.search_inventory()

    def _normalize_msg(self, error_val: Optional[Any], message_val: Optional[Any]) -> str:
        val = error_val if (isinstance(error_val, str) and error_val.strip()) else message_val
        if isinstance(val, str) and val.strip():
            return val.strip()
        return "No details provided by server."
