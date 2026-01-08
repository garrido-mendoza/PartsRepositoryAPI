# gui/main_gui.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from gui.widgets.parts_tab import PartsTab
from gui.widgets.locations_tab import LocationsTab
from gui.widgets.boxes_tab import BoxesTab
from gui.widgets.inventory_tab import InventoryTab
from gui.api_client import ApiClient

def start_app():
    app_qt = QApplication(sys.argv)
    client = ApiClient("http://127.0.0.1:8000")  # connect to backend

    window = QMainWindow()
    window.setWindowTitle("Parts Inventory GUI v1")

    tabs = QTabWidget()
    parts_tab = PartsTab(client)
    locations_tab = LocationsTab(client)
    boxes_tab = BoxesTab(client)
    inventory_tab = InventoryTab(client)

    tabs.addTab(parts_tab, "Parts")
    tabs.addTab(locations_tab, "Locations")
    tabs.addTab(boxes_tab, "Boxes")
    tabs.addTab(inventory_tab, "Inventory")

    # Connect tab change event
    def on_tab_changed(index):
        widget = tabs.widget(index)
        if isinstance(widget, InventoryTab):
            widget.refresh_locations()

    tabs.currentChanged.connect(on_tab_changed)

    window.setCentralWidget(tabs)
    window.resize(1000, 700)
    window.show()
    sys.exit(app_qt.exec())
