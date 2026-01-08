# test_workflow.py
from gui.api_client import ApiClient

def main():
    client = ApiClient("http://127.0.0.1:8000")

    print("=== Testing Locations ===")
    loc = client.add_location("204.1", "Diego's desk")
    print("Add Location:", loc)

    all_locs = client.list_locations()
    print("List Locations:", all_locs)

    print("\n=== Testing Parts ===")
    part = client.add_part("PN001", "O-RING")
    print("Add Part:", part)

    print("\n=== Testing Inventory ===")
    inv = client.add_inventory("BOX_A1", "PN001", "O-RING", "204.1", 5)
    print("Add Inventory:", inv)

    search_part = client.search_inventory("PN001")
    print("Search Inventory by Part:", search_part)

    search_box = client.search_inventory_by_box("BOX_A1")
    print("Search Inventory by Box:", search_box)

    if isinstance(inv, dict) and "inventory_id" in inv:
        inv_id = inv["inventory_id"]
        delete = client.delete_inventory(inv_id)
        print("Delete Inventory:", delete)

if __name__ == "__main__":
    main()
