from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

def fill_table(table: QTableWidget, rows: list[list]):
    """
    Fill a QTableWidget with the given rows of data.

    Args:
        table (QTableWidget): The table widget to populate.
        rows (list[list]): A list of rows, where each row is a list of cell values.
    """
    # Clear existing rows
    table.setRowCount(0)

    for row_idx, row_data in enumerate(rows):
        table.insertRow(row_idx)
        for col_idx, value in enumerate(row_data):
            item = QTableWidgetItem(str(value))
            table.setItem(row_idx, col_idx, item)
