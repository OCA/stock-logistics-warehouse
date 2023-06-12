import base64

from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource
from odoo.tests import tagged
from odoo.tests.common import SingleTransactionCase


@tagged("post_install", "-at_install")
class TestWizard(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Wizard = cls.env["stock.import"]
        cls.Header = cls.env["stock.import.header"]
        cls.MoveLine = cls.env["stock.move.line"]
        cls.Quant = cls.env["stock.quant"]
        cls.Product = cls.env["product.product"]
        # stock_inventory_discrepancy and this module conflict with each other
        # (in the tests)
        cls.is_stock_inv_discrepancy_installed = bool(
            cls.env["ir.module.module"].search(
                [
                    ("name", "=", "stock_inventory_discrepancy"),
                    ("state", "=", "installed"),
                ]
            )
        )
        if cls.is_stock_inv_discrepancy_installed:
            cls.ConfirmDiscrepancyWiz = cls.env["confirm.discrepancy.wiz"]

        def load_file(file_name: str):
            csv_file_path = get_module_resource(
                "stock_quant_import", "tests", file_name
            )
            with open(csv_file_path, "rb") as file:
                file_content = file.read()
            return base64.b64encode(file_content)

        cls.input_csv_1 = load_file("test1.csv")
        cls.input_csv_2 = load_file("test2.csv")
        cls.input_csv_3 = load_file("test3.csv")

        cls.default_loc = (
            cls.env["stock.warehouse"]
            .search([("company_id", "=", cls.env.company.id)], limit=1)
            .lot_stock_id
        )
        products = cls.Product.search([("default_code", "in", ["E-COM07", "E-COM11"])])
        cls.quants_search = [
            ("product_id", "in", products.ids),
            ("location_id", "=", cls.default_loc.id),
        ]
        cls.move_line_search = [
            ("product_id", "in", products.ids),
            "|",
            ("location_id", "=", cls.default_loc.id),
            ("location_dest_id", "=", cls.default_loc.id),
        ]

    def test_analyze_csv(self):
        wizard = self.Wizard.create({"file_import": self.input_csv_1})
        self.assertFalse(self.Header.search([("stock_import_id", "=", wizard.id)]))

        wizard.button_analyze_csv()
        self.assertTrue(self.Header.search([("stock_import_id", "=", wizard.id)]))

        self.assertTrue(wizard.internal_ref_col_id)
        self.assertTrue(wizard.quantity_col_id)

        wizard_1 = self.Wizard.create({"file_import": self.input_csv_2})

        # raises an exception because the second csv has less than 2 cols
        self.assertRaises(UserError, wizard_1.button_analyze_csv)

    def test_load_csv_data(self):
        wizard = self.Wizard.create({"file_import": self.input_csv_1})
        wizard.button_analyze_csv()
        # location id must be company's default warehouse location
        self.assertEqual(wizard.location_id, self.default_loc)

        product_move_lines_before = self.MoveLine.search(self.move_line_search)

        stock_quants = self.Quant.search(self.quants_search)
        old_quantity = stock_quants.mapped("quantity")
        wizard.button_load_csv_data()

        if self.is_stock_inv_discrepancy_installed:
            conflict = self.ConfirmDiscrepancyWiz.with_context(
                discrepancy_quant_ids=stock_quants.ids
            ).create({})
            conflict.with_context(active_ids=stock_quants.ids).button_apply()

        new_quantity = self.Quant.search(self.quants_search).mapped("quantity")
        self.assertTrue(old_quantity != new_quantity)

        product_move_lines_after = self.MoveLine.search(self.move_line_search)
        new_move_lines = product_move_lines_after - product_move_lines_before
        self.assertEqual(
            len(new_move_lines),
            2,
            "Move lines (chronology) were not updated correctly",
        )
        for line in new_move_lines:
            self.assertEqual(line.state, "done")
            self.assertEqual(line.reference, "Product Quantity Updated")

    def test_load_csv_data_strict_mode(self):
        wizard = self.Wizard.create(
            {"file_import": self.input_csv_1, "strict_mode": True}
        )
        wizard.button_analyze_csv()

        with self.assertRaises(UserError) as error:
            wizard.button_load_csv_data()

        self.assertTrue(
            "- test: Could not find product with this Internal Reference."
            in str(error.exception)
        )

        # Test for strict_mode with valid input file
        wizard_2 = self.Wizard.create(
            {"file_import": self.input_csv_3, "strict_mode": True}
        )
        wizard_2.button_analyze_csv()

        stock_quants = self.Quant.search(self.quants_search)
        old_quantity = stock_quants.mapped("quantity")
        wizard_2.button_load_csv_data()

        if self.is_stock_inv_discrepancy_installed:
            conflict = self.ConfirmDiscrepancyWiz.with_context(
                discrepancy_quant_ids=stock_quants.ids
            ).create({})
            conflict.with_context(active_ids=stock_quants.ids).button_apply()

        new_quantity = self.Quant.search(self.quants_search).mapped("quantity")
        self.assertTrue(old_quantity != new_quantity)
