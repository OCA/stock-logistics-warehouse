# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockQuantManualAssign(TransactionCase):
    def setUp(self):
        super(TestStockQuantManualAssign, self).setUp()
        self.quant_model = self.env["stock.quant"]
        self.picking_model = self.env["stock.picking"]
        self.location_model = self.env["stock.location"]
        self.move_model = self.env["stock.move"]
        self.quant_assign_wizard = self.env["assign.manual.quants"]
        self.ModelDataObj = self.env["ir.model.data"]
        self.product = self.env["product.product"].create(
            {"name": "Product 4 test", "type": "product"}
        )
        self.location_src = self.env.ref("stock.stock_location_locations_virtual")
        self.location_dst = self.env.ref("stock.stock_location_customers")
        self.picking_type_out = self.ModelDataObj._xmlid_to_res_id(
            "stock.picking_type_out"
        )
        self.env["stock.picking.type"].browse(
            self.picking_type_out
        ).reservation_method = "manual"
        self.location1 = self.location_model.create(
            {
                "name": "Location 1",
                "usage": "internal",
                "location_id": self.location_src.id,
            }
        )
        self.location2 = self.location_model.create(
            {
                "name": "Location 2",
                "usage": "internal",
                "location_id": self.location_src.id,
            }
        )
        self.location3 = self.location_model.create(
            {
                "name": "Location 3",
                "usage": "internal",
                "location_id": self.location_src.id,
            }
        )
        self.picking_type = self.env.ref("stock.picking_type_out")
        self.quant1 = self.quant_model.sudo().create(
            {
                "product_id": self.product.id,
                "quantity": 100.0,
                "location_id": self.location1.id,
            }
        )
        self.quant2 = self.quant_model.sudo().create(
            {
                "product_id": self.product.id,
                "quantity": 100.0,
                "location_id": self.location2.id,
            }
        )
        self.quant3 = self.quant_model.sudo().create(
            {
                "product_id": self.product.id,
                "quantity": 100.0,
                "location_id": self.location3.id,
            }
        )
        self.move = self.move_model.create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 400.0,
                "product_uom": self.product.uom_id.id,
                "location_id": self.location_src.id,
                "location_dest_id": self.location_dst.id,
                "picking_type_id": self.picking_type.id,
            }
        )
        self.move._action_confirm()

    def test_quant_assign_wizard(self):
        wizard = self.quant_assign_wizard.with_context(active_id=self.move.id).create(
            {}
        )
        self.assertEqual(
            len(wizard.quants_lines.ids),
            3,
            "Three quants created, three quants got by default",
        )
        self.assertEqual(
            len(wizard.quants_lines.filtered("selected").ids),
            0,
            "None of the quants must have been selected",
        )
        self.assertEqual(wizard.lines_qty, 0.0, "None selected must give 0")
        self.assertEqual(
            sum(line.qty for line in wizard.quants_lines),
            self.move.reserved_availability,
        )
        self.assertEqual(wizard.move_qty, self.move.product_uom_qty)

    def test_quant_assign_wizard_constraint(self):
        wizard = self.quant_assign_wizard.with_context(active_id=self.move.id).create(
            {}
        )
        self.assertEqual(
            len(wizard.quants_lines.ids),
            3,
            "Three quants created, three quants got by default",
        )
        self.assertEqual(
            len(wizard.quants_lines.filtered("selected").ids),
            0,
            "None of the quants must have been selected",
        )
        self.assertEqual(wizard.lines_qty, 0.0, "None selected must give 0")
        with self.assertRaises(ValidationError):
            wizard.write(
                {
                    "quants_lines": [
                        (1, wizard.quants_lines[:1].id, {"selected": True, "qty": 500})
                    ]
                }
            )

    def test_quant_manual_assign(self):
        wizard = self.quant_assign_wizard.with_context(active_id=self.move.id).create(
            {}
        )
        self.assertEqual(
            len(wizard.quants_lines.ids),
            3,
            "Three quants created, three quants got by default",
        )
        wizard.quants_lines[0].write({"selected": True})
        wizard.quants_lines[0]._onchange_selected()
        wizard.quants_lines[1].write({"selected": True, "qty": 50.0})
        self.assertEqual(wizard.lines_qty, 150.0)
        self.assertEqual(wizard.move_qty, 250.0)
        wizard.assign_quants()
        self.assertAlmostEqual(
            len(self.move.move_line_ids),
            2,
            "There are 2 quants selected",
        )
        self.assertFalse(self.move.picking_type_id.auto_fill_qty_done)
        self.assertEqual(sum(self.move.move_line_ids.mapped("qty_done")), 0.0)

    def test_quant_manual_assign_auto_fill_qty_done(self):
        wizard = self.quant_assign_wizard.with_context(active_id=self.move.id).create(
            {}
        )
        wizard.quants_lines[0].write({"selected": True})
        wizard.quants_lines[0]._onchange_selected()
        wizard.quants_lines[1].write({"selected": True, "qty": 50.0})
        self.assertEqual(wizard.lines_qty, 150.0)
        self.picking_type.auto_fill_qty_done = True
        wizard.assign_quants()
        self.assertTrue(self.move.picking_type_id.auto_fill_qty_done)
        self.assertEqual(sum(self.move.move_line_ids.mapped("qty_done")), 150.0)

    def test_quant_assign_wizard_after_availability_check(self):
        self.move._action_assign()
        wizard = self.quant_assign_wizard.with_context(active_id=self.move.id).create(
            {}
        )
        self.assertEqual(
            len(wizard.quants_lines.ids),
            3,
            "Three quants created, three quants got by default",
        )
        self.assertEqual(
            len(wizard.quants_lines.filtered("selected").ids),
            3,
            "All the quants must have been selected",
        )
        self.assertEqual(wizard.lines_qty, 300.0)
        self.assertEqual(wizard.move_qty, 100.0)
        self.assertEqual(
            len(wizard.quants_lines.filtered("selected")), len(self.move.move_line_ids)
        )
        self.assertEqual(
            sum(line.qty for line in wizard.quants_lines),
            self.move.reserved_availability,
        )
