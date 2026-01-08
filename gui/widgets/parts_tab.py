from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from gui.common.dialogs import confirm

class PartsTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        layout = QVBoxLayout(self)

        # Controls
        ctl = QHBoxLayout()
        self.part_number = QLineEdit()
        self.part_number.setPlaceholderText("Part Number")
        self.description = QLineEdit()
        self.description.setPlaceholderText("Description")
        btn_add = QPushButton("Add Part")
        btn_search = QPushButton("Search Part")
        btn_delete = QPushButton("Delete Selected")
        btn_show = QPushButton("Show Parts")
        ctl.addWidget(self.part_number)
        ctl.addWidget(self.description)
        ctl.addWidget(btn_add)
        ctl.addWidget(btn_search)
        ctl.addWidget(btn_delete)
        ctl.addWidget(btn_show)
        layout.addLayout(ctl)

        # Table (only show Part Number + Description)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Part Number", "Description"])
        layout.addWidget(self.table)

        # Events
        btn_add.clicked.connect(self.add_part)
        btn_search.clicked.connect(self.search_part)
        btn_delete.clicked.connect(self.delete_selected)
        btn_show.clicked.connect(self.show_parts)

    def add_part(self):
        pn = self.part_number.text().strip()
        desc = self.description.text().strip()
        if not pn or not desc:
            return
        result = self.client.add_part(pn, desc)
        # Show popup if backend returns a message or error
        if isinstance(result, dict) and ("error" in result or "message" in result):
            msg = result.get("error") or result.get("message") or "Unknown response from server."
            QMessageBox.information(self, "Add Part", str(msg))
        self.search_part()

    def search_part(self):
        pn = self.part_number.text().strip()
        if not pn:
            return
        d = self.client.search_part(pn)
        self.table.setRowCount(0)
        if isinstance(d, dict) and all(k in d for k in ("part_id", "part_number", "description")):
            self.table.insertRow(0)
            pn_item = QTableWidgetItem(d["part_number"])
            desc_item = QTableWidgetItem(d["description"])
            # Store hidden part_id in the first column item
            pn_item.setData(32, d["part_id"])  # 32 = Qt.UserRole
            self.table.setItem(0, 0, pn_item)
            self.table.setItem(0, 1, desc_item)

    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if item is None:
            return
        part_id = item.data(32)  # retrieve hidden ID
        if not confirm("Delete Part", f"Delete part ID {part_id}?"):
            return
        self.client.delete_part(part_id)
        self.table.removeRow(row)

    def show_parts(self):
        # 1. Trigger backend console print
        result = self.client.get("/parts/print")

        # 2. Fetch all parts for the GUI table
        data = self.client.list_parts()

        if not isinstance(data, list):
            msg = data.get("error") or data.get("message") or "Unknown error"
            QMessageBox.information(self, "Show Parts", msg)
            return

        # 3. Populate the table
        self.table.setRowCount(0)
        for row, p in enumerate(data):
            self.table.insertRow(row)
            pn_item = QTableWidgetItem(p["part_number"])
            desc_item = QTableWidgetItem(p["description"])
            pn_item.setData(32, p["part_id"])  # hidden ID
            self.table.setItem(row, 0, pn_item)
            self.table.setItem(row, 1, desc_item)

        # 4. Show confirmation popup
        msg = result.get("message") or result.get("error") or "Done"
        QMessageBox.information(self, "Show Parts", msg)

