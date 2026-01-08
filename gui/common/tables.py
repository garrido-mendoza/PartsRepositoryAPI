from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

def fill_table(table: QTableWidget, rows: list[list[str]]):
    table.clearContents()
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            table.setItem(r, c, QTableWidgetItem(str(val)))
