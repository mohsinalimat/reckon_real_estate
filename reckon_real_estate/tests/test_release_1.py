import frappe
from frappe.tests.utils import FrappeTestCase

class TestRelease1(FrappeTestCase):
    def test_app_imports(self):
        import reckon_real_estate
        self.assertTrue(reckon_real_estate.__version__)

    def test_unit_price_calculation(self):
        doc = frappe.new_doc("Real Estate Unit")
        doc.unit_code = "TEST-UNIT-001"
        doc.unit_no = "T-001"
        doc.project = self._project()
        doc.building = self._building(doc.project)
        doc.floor = self._floor(doc.project, doc.building)
        doc.unit_type = "Apartment"
        doc.area_sqft = 1000
        doc.base_rate_per_sqft = 5000
        item_code = "TEST-REAL-ESTATE-UNIT"
        if not frappe.db.exists("Item", item_code):
            frappe.get_doc({
                "doctype": "Item", "item_code": item_code,
                "item_name": "Test Real Estate Unit", "is_stock_item": 0,
                "item_group": "All Item Groups", "stock_uom": "Nos",
            }).insert()
        doc.erpnext_item = item_code
        doc.insert()
        self.assertEqual(doc.list_price, 5000000)

    def _project(self):
        name = frappe.db.exists("Real Estate Project", {"project_code": "TEST-PROJ-001"})
        if name:
            return name
        company = frappe.db.get_value("Company", {}, "name")
        return frappe.get_doc({
            "doctype":"Real Estate Project",
            "project_code":"TEST-PROJ-001",
            "project_name":"Test Project",
            "company":company,
            "project_type":"Residential",
            "status":"Active"
        }).insert().name

    def _building(self, project):
        name = frappe.db.exists("Real Estate Building", {"building_code":"TEST-BLD-001"})
        if name:
            return name
        return frappe.get_doc({
            "doctype":"Real Estate Building",
            "building_code":"TEST-BLD-001",
            "building_name":"Test Building",
            "project":project
        }).insert().name

    def _floor(self, project, building):
        name = frappe.db.exists("Real Estate Floor", {"floor_code":"TEST-FLR-001"})
        if name:
            return name
        return frappe.get_doc({
            "doctype":"Real Estate Floor",
            "floor_code":"TEST-FLR-001",
            "floor_name":"Floor 1",
            "project":project,
            "building":building,
            "floor_number":1
        }).insert().name
