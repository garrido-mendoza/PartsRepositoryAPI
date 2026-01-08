from PySide6.QtWidgets import QMessageBox
#from PySide6.QtWidgets import QMessageBox, QMessageBox.StandardButton

def confirm(title: str, message: str) -> bool:
    """
    Show a Yes/No confirmation dialog.
    Returns True if user clicks Yes, False otherwise.
    """
    box = QMessageBox()
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    box.setDefaultButton(QMessageBox.StandardButton.No)
    result = box.exec()
    return result == QMessageBox.StandardButton.Yes
