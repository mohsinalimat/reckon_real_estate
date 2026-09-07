import importlib.util
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


class Row(dict):
    def __getattr__(self, key):
        return self.get(key)


class TestDisplayNames(unittest.TestCase):
    def setUp(self):
        self.frappe = ModuleType('frappe')
        self.frappe.db = Mock()
        self.frappe.has_permission = Mock(return_value=True)
        self.frappe.get_list = Mock(return_value=[])
        self.frappe.clear_cache = Mock()
        spec=importlib.util.spec_from_file_location('display_names_test',ROOT/'display_names.py')
        self.module=importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules',{'frappe':self.frappe}):
            spec.loader.exec_module(self.module)

    def booking(self):
        fields={'customer':SimpleNamespace(fieldtype='Link',options='Customer'),
                'unit':SimpleNamespace(fieldtype='Link',options='Real Estate Unit'),
                'project':SimpleNamespace(fieldtype='Link',options='Real Estate Project')}
        return Row(doctype='Property Booking',name='PB-001',customer='C1',unit='U1',project='P1',booking_date='2026-09-07',
                   meta=SimpleNamespace(get_field=lambda key:fields.get(key)))

    def test_descriptive_title_keeps_original_ids(self):
        doc=self.booking()
        labels={'C1':'Rahim','U1':'A501','P1':'Lake View'}
        title=self.module.make_record_title(doc,lambda dt,name,field:labels[name])
        self.assertEqual(title,'Rahim — A501 — Lake View — 2026-09-07')
        self.assertEqual(doc.unit,'U1')
        self.assertEqual(doc.name,'PB-001')

    def test_missing_names_have_safe_fallback_and_length_bound(self):
        doc=self.booking()
        title=self.module.make_record_title(doc,lambda *args:None)
        self.assertIn('U1',title)
        self.assertLessEqual(len(self.module.make_record_title(doc,lambda *args:'Long name '*100)),140)

    def test_all_app_lists_have_names_and_ids_without_renaming(self):
        count=0
        for path in (ROOT/'reckon_real_estate/doctype').glob('*/*.json'):
            meta=json.loads(path.read_text(encoding='utf-8'))
            if meta.get('istable'):continue
            count+=1
            self.assertTrue(meta['show_title_field_in_link'],meta['name'])
            fields={f['fieldname']:f for f in meta['fields']}
            self.assertIn(meta['title_field'],fields)
            self.assertTrue(fields[meta['title_field']]['in_list_view'])
            self.assertIn('hide_name_column: false',path.with_name(path.stem+'_list.js').read_text())
            self.assertNotEqual(meta['autoname'],'field:'+meta['title_field'])
        self.assertEqual(count,25)

    def test_report_adds_names_and_preserves_ids_and_summary(self):
        self.frappe.get_list.return_value=[Row(name='P1',project_name='Lake View')]
        columns=[{'fieldname':'project','fieldtype':'Link','options':'Real Estate Project','label':'Project'}]
        summary=[{'label':'Amount','value':100}]
        report=self.module.with_link_names(lambda:(columns,[Row(project='P1',amount=100)],None,None,summary))
        result=report()
        self.assertEqual(result[0][0]['label'],'Project Name')
        self.assertEqual(result[0][1]['label'],'Project ID')
        self.assertEqual(result[1][0].project,'P1')
        self.assertEqual(result[1][0].project_display_name,'Lake View')
        self.assertIs(result[4],summary)

    def test_report_does_not_fetch_restricted_names(self):
        self.frappe.has_permission.return_value=False
        report=self.module.with_link_names(lambda:([{'fieldname':'project','fieldtype':'Link','options':'Real Estate Project','label':'Project'}],[Row(project='P1')]))
        self.assertEqual(report()[1][0].project_display_name,'P1')
        self.frappe.get_list.assert_not_called()

    def test_dynamic_source_links_receive_readable_titles(self):
        self.frappe.get_list.return_value=[Row(name='PB1',record_title='Rahim — A501')]
        report=self.module.with_link_names(lambda:([{'fieldname':'source','fieldtype':'Dynamic Link','options':'source_type','label':'Source'}],[Row(source_type='Property Booking',source='PB1')]))
        row=report()[1][0]
        self.assertEqual(row.source,'PB1')
        self.assertEqual(row.source_display_name,'Rahim — A501')

    def test_backfill_updates_only_display_field_without_saving(self):
        doc=self.booking()
        self.frappe.get_doc=Mock(return_value=doc)
        self.frappe.get_all=Mock(side_effect=[['PB-001'],[]])
        self.frappe.db.get_value.return_value='Readable name'
        setter=ModuleType('frappe.custom.doctype.property_setter.property_setter')
        setter.make_property_setter=Mock()
        with patch.dict('sys.modules',{'frappe.custom.doctype.property_setter.property_setter':setter}), patch.object(self.module,'NATIVE_TITLES',{}), patch.object(self.module,'TRANSACTION_TITLES',{'Property Booking':('customer','unit')}):
            self.module.setup_display_names()
        call=self.frappe.db.set_value.call_args
        self.assertEqual(call.args[:3],('Property Booking','PB-001','record_title'))
        self.assertEqual(call.kwargs,{'update_modified':False})
