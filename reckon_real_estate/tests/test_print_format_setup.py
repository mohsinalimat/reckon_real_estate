import importlib.util
from pathlib import Path
from types import ModuleType
import unittest
from unittest.mock import Mock, patch


class TestPrintFormatSetup(unittest.TestCase):
    def setUp(self):
        self.frappe = ModuleType("frappe")
        self.frappe.db = Mock()
        self.frappe.reload_doc = Mock()
        self.frappe.clear_cache = Mock()
        path = Path(__file__).resolve().parents[1] / "setup/install.py"
        spec = importlib.util.spec_from_file_location("print_format_setup_under_test", path)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", {"frappe": self.frappe}):
            spec.loader.exec_module(self.module)

    def test_restores_only_missing_detailed_format(self):
        self.frappe.db.exists.side_effect = lambda dt, name: name == "Sales Agreement"
        self.module.ensure_agreement_print_formats()
        self.frappe.reload_doc.assert_called_once_with(
            "reckon_real_estate", "print_format", "detailed_sales_agreement", force=True
        )
        self.frappe.clear_cache.assert_called_once_with(doctype="Sales Agreement")

    def test_existing_formats_are_not_overwritten(self):
        self.frappe.db.exists.return_value = True
        self.module.ensure_agreement_print_formats()
        self.frappe.reload_doc.assert_not_called()

    def test_both_missing_formats_are_restored(self):
        self.frappe.db.exists.return_value = False
        self.module.ensure_agreement_print_formats()
        self.assertEqual(self.frappe.reload_doc.call_count, 2)

    def test_install_and_migrate_restore_formats_before_validation(self):
        for hook in (self.module.after_install, self.module.after_migrate):
            calls = []
            names = ["ensure_app_roles", "ensure_app_role_permissions", "ensure_desk_navigation",
                     "cleanup_legacy_modules", "cleanup_legacy_reports", "ensure_erpnext_custom_fields",
                     "ensure_home_analytics", "ensure_agreement_print_formats", "validate_installation"]
            display = ModuleType("reckon_real_estate.display_names")
            display.setup_display_names = Mock()
            with patch.dict("sys.modules", {"reckon_real_estate.display_names": display}), patch.multiple(self.module, **{
                name: Mock(side_effect=lambda n=name: calls.append(n)) for name in names
            }):
                hook()
                display.setup_display_names.assert_called_once()
            self.assertEqual(calls[-2:], ["ensure_agreement_print_formats", "validate_installation"])
