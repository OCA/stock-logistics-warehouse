# Copyright 2024 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestStockException(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.res_users_model = cls.env["res.users"]
        cls.product_model = cls.env["product.product"]
        cls.exception_rule = cls.env["exception.rule"]

        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.picking_type_id = cls.env.ref("stock.picking_type_out")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        # Create a product:
        cls.product_1 = cls.product_model.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "default_code": "PROD1",
                "uom_id": cls.uom_unit.id,
            }
        )

        # Create a Picking:
        cls.picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "picking_type_id": cls.picking_type_id.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product_1.name,
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product_1.uom_id.id,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    )
                ],
            }
        )

    def test01_confirm_picking_fail_by_py(self):
        self.stock_exception = self.exception_rule.create(
            {
                "name": "No Partner",
                "sequence": 10,
                "model": "stock.picking",
                "exception_type": "by_py_code",
                "code": "if not self.partner_id: failed=True",
            }
        )
        exception_action = self.picking.action_confirm()
        self.assertEqual(exception_action.get("res_model"), "stock.exception.confirm")
        self.assertTrue(self.picking.exceptions_summary)
        self.assertTrue(self.picking.exception_ids)
        rules = self.env["exception.rule"].browse(self.picking.exception_ids.ids)
        self.assertIn(self.picking.id, rules.mapped("picking_ids.id"))

        self.picking.button_validate()
        self.assertTrue(self.picking.exceptions_summary)

        # Test ignore exception make possible for the picking to validate
        self.assertEqual(self.picking.state, "draft")
        self.picking.action_ignore_exceptions()
        self.assertTrue(self.picking.ignore_exception)
        self.assertFalse(self.picking.exceptions_summary)
        self.picking.action_confirm()
        self.assertEqual(self.picking.state, "confirmed")

    def test02_confirm_picking_fail_by_domain(self):
        self.exception_method = self.env["exception.rule"].create(
            {
                "name": "No Partner",
                "sequence": 11,
                "model": "stock.picking",
                "domain": "[('partner_id', '=', False)]",
                "exception_type": "by_domain",
            }
        )
        exception_action = self.picking.action_confirm()
        self.assertEqual(exception_action.get("res_model"), "stock.exception.confirm")
        self.assertTrue(self.picking.exceptions_summary)
        self.assertTrue(self.picking.exception_ids)
        exception_form = Form(
            self.env["stock.exception.confirm"].with_context(
                **exception_action.get("context")
            ),
        )
        stock_exception = exception_form.save()
        stock_exception.ignore = True
        stock_exception.action_confirm()

    def test03_call_picking_method(self):
        self.env["stock.picking"].test_all_draft_pickings()
        self.env["stock.picking"]._reverse_field()
        self.picking.move_ids._get_main_records()
        self.picking.move_ids._reverse_field()

    def test_confirm_picking(self):
        self.assertEqual(self.picking.state, "draft")
        self.picking.action_confirm()
        self.assertEqual(self.picking.state, "confirmed")
