import importlib.util
import json
from pathlib import Path
from types import ModuleType
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


class Record(dict):
    def __getattr__(self, key):
        return self.get(key)

    def set(self, key, value):
        self[key] = value

    def check_permission(self, permission):
        pass


class TestAgreementDefaults(unittest.TestCase):
    def setUp(self):
        self.frappe = ModuleType('frappe')
        self.frappe.whitelist = lambda: lambda fn: fn
        self.frappe.has_permission = Mock(return_value=True)
        self.frappe.PermissionError = PermissionError
        self.frappe.throw = Mock(side_effect=PermissionError('Denied'))
        self.frappe.get_all = Mock(return_value=[])
        spec = importlib.util.spec_from_file_location('agreement_defaults_test', ROOT / 'agreement_defaults.py')
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', {'frappe': self.frappe}):
            spec.loader.exec_module(self.module)
        self.records = {
            ('Property Booking','B'): Record(name='B', customer='C', project='P', unit='U', contract_value=100, discount=5, net_contract_value=95, booking_money=10),
            ('Company','CO'): Record(name='CO', company_name='Example Developer'),
            ('Customer','C'): Record(name='C', customer_name='Buyer', tax_id='NOT-AN-NID'),
            ('Real Estate Project','P'): Record(name='P', project_name='Project', company='CO', address='Dhaka', expected_completion_date='2027-01-01'),
            ('Real Estate Unit','U'): Record(name='U', unit_no='A501', building='BL', floor='FL', area_sqft=1000, erpnext_item='ITEM', description='<p>Unit specifications</p>'),
            ('Real Estate Building','BL'): Record(name='BL', building_name='Building A'),
            ('Real Estate Floor','FL'): Record(name='FL', floor_name='Fifth Floor'),
            ('Item','ITEM'): Record(name='ITEM', item_name='Apartment Product'),
        }
        self.frappe.get_doc = lambda dt, name: self.records[dt, name]

    def test_booking_maps_master_details_without_inventing_identity(self):
        values = self.module.get_agreement_defaults('B')
        self.assertEqual(values['net_contract_value'],95)
        self.assertEqual(values['seller_legal_name'],'Example Developer')
        self.assertEqual(values['buyer_name'],'Buyer')
        self.assertIsNone(values['buyer_nid_passport'])
        self.assertIsNone(values['authorized_signatory'])
        self.assertIn('Building A',values['property_description'])
        self.assertIn('Fifth Floor',values['property_description'])
        self.assertIn('Apartment Product',values['property_description'])
        self.assertEqual(values['included_facilities'],'<p>Unit specifications</p>')

    def test_addresses_contacts_and_custom_identity(self):
        self.records['Customer','C'].update(customer_primary_address='ADDR', customer_primary_contact='CONTACT', custom_national_id='123')
        self.records['Address','ADDR'] = Record(address_line1='Road 1', city='Dhaka',country='Bangladesh')
        self.records['Contact','CONTACT'] = Record(mobile_no='01700000000',email_id='sample@example.test')
        self.frappe.get_all.side_effect = lambda dt, filters, pluck: [] if filters['link_doctype']=='Company' else ['ADDR'] if filters['parenttype']=='Address' else ['CONTACT']
        values = self.module.get_agreement_defaults('B')
        self.assertEqual(values['buyer_address'],'Road 1, Dhaka, Bangladesh')
        self.assertEqual(values['buyer_phone'],'01700000000')
        self.assertEqual(values['buyer_email'],'sample@example.test')
        self.assertEqual(values['buyer_nid_passport'],'123')

    def test_manual_terms_are_preserved(self):
        doc = Record(payment_default_terms='Negotiated clause',buyer_address='Agreed notice address')
        self.module.fill_empty_fields(doc,self.module.get_agreement_defaults('B'))
        self.assertEqual(doc.payment_default_terms,'Negotiated clause')
        self.assertEqual(doc.buyer_address,'Agreed notice address')
        self.assertTrue(doc.handover_conditions)

    def test_snapshot_escapes_master_text(self):
        self.records['Real Estate Unit','U']['unit_no']='<script>alert(1)</script>'
        value=self.module.get_agreement_defaults('B')['property_description']
        self.assertNotIn('<script>',value)
        self.assertIn('&lt;script&gt;',value)

    def test_permission_is_required(self):
        self.frappe.has_permission.return_value=False
        with self.assertRaises(PermissionError):
            self.module.get_agreement_defaults('B')

    def test_terms_can_load_before_booking_and_prints_include_snapshot(self):
        values=self.module.get_agreement_defaults()
        self.assertNotIn('customer',values)
        self.assertIn('Bangladesh',values['terms'])
        for name in ('sales_agreement','detailed_sales_agreement'):
            path=ROOT / f'reckon_real_estate/print_format/{name}/{name}.json'
            html=json.loads(path.read_text(encoding='utf-8'))['html']
            self.assertIn("doc.get('property_description')",html)
            for field in ('handover_conditions','utility_maintenance_terms','defect_liability_terms','registration_document_terms','dispute_resolution_terms','annexure_documents'):
                self.assertIn('doc.'+field,html)
