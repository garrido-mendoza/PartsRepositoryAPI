from urllib import response
import requests

class ApiClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url

    # ---------------- Parts ----------------
    def add_part(self, part_number, description):
        response = requests.post(
            f"{self.base_url}/parts/",
            json={"part_number": part_number, "description": description}
        )
        try:
            return response.json()
        except ValueError:
            return {"message": response.text}

    def search_part(self, part_number: str):
        """Search for a part by its part_number using the backend route."""
        try:
            response = requests.get(f"{self.base_url}/parts/by_number/{part_number}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def delete_part(self, part_id):
        response = requests.delete(f"{self.base_url}/parts/{part_id}")
        try:
            return response.json()
        except ValueError:
            return {"message": response.text}

    def list_parts(self):
        try:
            response = requests.get(f"{self.base_url}/parts/all")
            response.raise_for_status()
            return response.json()
        except ValueError:
            return {"message": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        

    # ---------------- Inventory ----------------
    def add_inventory(self, box_id, part_number, description, location_name, quantity):
        """Add inventory using box_id, part_number, description, and location_name."""
        response = requests.post(
            f"{self.base_url}/inventory/",
            json={
                "box_id": box_id,
                "part_number": part_number,
                "description": description,
                "location_name": location_name,
                "quantity": quantity
            }
        )
        try:
            return response.json()
        except ValueError:
            return {"message": response.text}

    def search_inventory(self, part_number):
        """Search inventory by part_number."""
        response = requests.get(f"{self.base_url}/inventory/search", params={"part_number": part_number})
        try:
            return response.json()
        except ValueError:
            return {"message": response.text}

    def search_inventory_by_box(self, box_code):
        """Search inventory by box_code (string)."""
        try:
            response = requests.get(f"{self.base_url}/inventory/search_by_box/{box_code}")
            response.raise_for_status()
            return response.json()
        except ValueError:
            return {"message": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def delete_inventory(self, inventory_id):
        response = requests.delete(f"{self.base_url}/inventory/{inventory_id}")
        try:
            return response.json()
        except ValueError:
            return {"message": response.text}

    def update_inventory(self, inventory_id, part_number, description, quantity):
        """
        Update Inventory: commit adjustments to an existing inventory record.
        """
        try:
            payload = {
                "part_number": part_number,
                "description": description,
                "quantity": quantity
            }
            response = requests.put(f"{self.base_url}/inventory/{inventory_id}", json=payload)
            response.raise_for_status()
            return response.json()
        except ValueError:
            return {"message": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    # ---------------- Locations ----------------
    def add_location(self, location_name, description):
        response = requests.post(
            f"{self.base_url}/locations/",
            json={"location_name": location_name, "description": description}
        )
        try:
            return response.json()
        except ValueError:
            return {"message": response.text}

    def search_location(self, location_name):
        """Search location by name using /locations/search."""
        response = requests.get(f"{self.base_url}/locations/search", params={"location_name": location_name})
        try:
            return response.json()
        except ValueError:
            return {"message": response.text}

    def list_locations(self):
        """Return all locations using /locations/all."""
        try:
            response = requests.get(f"{self.base_url}/locations/all")
            response.raise_for_status()
            return response.json()
        except ValueError:
            return {"message": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def delete_location(self, location_id):
        response = requests.delete(f"{self.base_url}/locations/{location_id}")
        try:
            return response.json()
        except ValueError:
            return {"message": response.text}
    
    def get(self, path: str):
        try:
            response = requests.get(f"{self.base_url}{path}")
            response.raise_for_status()
            return response.json()
        except ValueError:
            return {"message": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    # ---------------- Boxes ----------------
    def add_box(self, code, location_name):
        """Add a box using its code and location_name (operator-friendly)."""
        try:
            response = requests.post(
                f"{self.base_url}/boxes/",
                json={"code": code, "location_name": location_name}
            )
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                return {"message": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def search_box(self, code):
        """Search for a box by its code using /boxes/search."""
        response = requests.get(f"{self.base_url}/boxes/search", params={"code": code})
        try:
            return response.json()
        except ValueError:
            return {"message": response.text}

    def delete_box(self, box_id):
        response = requests.delete(f"{self.base_url}/boxes/{box_id}")
        try:
            return response.json()
        except ValueError:
            return {"message": response.text}
