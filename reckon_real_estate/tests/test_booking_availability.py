import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch


class TestBookingAvailability(unittest.TestCase):
    def setUp(self):
        frappe = ModuleType('frappe')
        frappe.utils = SimpleNamespace(flt=lambda x: float(x or 0))
        frappe.throw = lambda message: (_ for _ in ()).throw(ValueError(message))
        self.unit = SimpleNamespace(project='P1',status='Available',docstatus=1)
        self.project = SimpleNamespace(status='Active',docstatus=1)
        frappe.get_doc = lambda dt, name: self.unit if dt == 'Real Estate Unit' else self.project
        frappe.db = SimpleNamespace(exists=Mock(side_effect=lambda dt,*args: True if dt=='Customer' else None))
        self.frappe = frappe
        document = ModuleType('frappe.model.document')
        document.Document = object
        workflow = ModuleType('reckon_real_estate.construction_workflow')
        for name in ('block_if_submitted','require_submitted','set_cancelled_status','set_draft_status','set_submitted_status'):
            setattr(workflow,name,Mock())
        path = Path(__file__).resolve().parents[1] / 'reckon_real_estate/doctype/property_booking/property_booking.py'
        spec = importlib.util.spec_from_file_location('booking_test_controller',path)
        module = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules',{'frappe':frappe,'frappe.model.document':document,'reckon_real_estate.construction_workflow':workflow}):
            spec.loader.exec_module(module)
        self.doc = module.PropertyBooking()
        self.doc.__dict__.update(name='B1',project='P1',unit='U1',customer='C1',contract_value=100,discount=0,docstatus=0)
        self.doc.get_doc_before_save = lambda: None

    def test_available_unit_in_active_project_is_accepted(self):
        self.doc.validate()
        self.assertEqual(self.doc.net_contract_value,100)

    def test_inactive_or_unsubmitted_project_is_rejected(self):
        for status,docstatus in [('Planning',1),('On Hold',1),('Completed',1),('Active',0),('Active',2)]:
            self.project.status,self.project.docstatus = status,docstatus
            with self.assertRaisesRegex(ValueError,'active, submitted'):
                self.doc.validate()

    def test_unavailable_or_unsubmitted_units_are_rejected(self):
        for status,docstatus in [('Booked',1),('Reserved',1),('Blocked',1),('Handed Over',1),('Available',0),('Available',2)]:
            self.unit.status,self.unit.docstatus = status,docstatus
            with self.assertRaisesRegex(ValueError,'available, submitted'):
                self.doc.validate()

    def test_other_project_unit_is_rejected(self):
        self.unit.project = 'P2'
        with self.assertRaisesRegex(ValueError,'selected Project'):
            self.doc.validate()

    def test_saved_draft_is_rechecked_on_submission_and_excludes_itself(self):
        self.doc.get_doc_before_save = lambda: SimpleNamespace(docstatus=0)
        self.doc.docstatus = 1
        self.doc.validate()
        filters = self.frappe.db.exists.call_args.args[1]
        self.assertEqual(filters['name'],['!=','B1'])
        self.unit.status = 'Booked'
        with self.assertRaisesRegex(ValueError,'available, submitted'):
            self.doc.validate()

    def test_existing_submitted_booking_keeps_its_booked_unit(self):
        self.doc.get_doc_before_save = lambda: SimpleNamespace(docstatus=1)
        self.doc.docstatus = 1
        self.unit.status = 'Booked'
        self.doc.validate()
