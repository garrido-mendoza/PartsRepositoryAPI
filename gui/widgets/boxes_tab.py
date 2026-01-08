from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from gui.common.dialogs import confirm

class BoxesTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        layout = QVBoxLayout(self)

        # Controls (horizontal layout to match other tabs)
        ctl = QHBoxLayout()
        self.box_label = QLineEdit()
        self.box_label.setPlaceholderText("Box Code")
        self.location_name = QLineEdit()
        self.location_name.setPlaceholderText("Location Name")
        btn_add = QPushButton("Add Box")
        btn_search = QPushButton("Search Box")
        btn_delete = QPushButton("Delete Selected")
        btn_show = QPushButton("Show Boxes")
        ctl.addWidget(self.box_label)
        ctl.addWidget(self.location_name)
        ctl.addWidget(btn_add)
        ctl.addWidget(btn_search)
        ctl.addWidget(btn_delete)
        ctl.addWidget(btn_show)
        layout.addLayout(ctl)

        # Table (only show Box Code + Location Name)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Box Code", "Location Name"])
        layout.addWidget(self.table)

        # Events
        btn_add.clicked.connect(self.add_box)
        btn_search.clicked.connect(self.search_box)
        btn_delete.clicked.connect(self.delete_selected)
        btn_show.clicked.connect(self.show_boxes)

    def add_box(self):
        label = self.box_label.text().strip()
        loc_name = self.location_name.text().strip()
        if not label or not loc_name:
            return
        result = self.client.add_box(label, loc_name)
        if isinstance(result, dict) and ("error" in result or "message" in result):
            msg = result.get("error") or result.get("message") or "Unknown response from server."
            QMessageBox.information(self, "Add Box", str(msg))
        self.search_box()

    def search_box(self):
        label = self.box_label.text().strip()
        if not label:
            return
        d = self.client.search_box(label)
        self.table.setRowCount(0)
        if isinstance(d, dict) and all(k in d for k in ("box_id", "code", "location_name")):
            self.table.insertRow(0)
            code_item = QTableWidgetItem(d["code"])
            loc_item = QTableWidgetItem(d["location_name"])
            code_item.setData(32, d["box_id"])  # 32 = Qt.UserRole
            self.table.setItem(0, 0, code_item)
            self.table.setItem(0, 1, loc_item)

    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if item is None:
            return
        box_id = item.data(32)  # retrieve hidden ID
        if not confirm("Delete Box", f"Delete box ID {box_id}?"):
            return
        self.client.delete_box(box_id)
        self.table.removeRow(row)

    def show_boxes(self):
        result = self.client.get("/boxes/print")
        QMessageBox.information(self, "Show Boxes", result.get("message", "Done"))