# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockQuantManualAssign(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.quant_model = cls.env["stock.quant"]
        cls.picking_model = cls.env["stock.picking"]
        cls.location_model = cls.env["stock.location"]
        cls.move_model = cls.env["stock.move"]
        cls.quant_assign_wizard = cls.env["assign.manual.quants"]
        cls.ModelDataObj = cls.env["ir.model.data"]
        cls.product = cls.env["product.product"].create(
            {"name": "Product 4 test", "type": "product"}
        )
        cls.location_src = cls.env.ref("stock.stock_location_locations_virtual")
        cls.location_dst = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.ModelDataObj._xmlid_to_res_id(
            "stock.picking_type_out"
        )
        cls.env["stock.picking.type"].browse(
            cls.picking_type_out
        ).reservation_method = "manual"
        cls.location1 = cls.location_model.create(
            {
                "name": "Location 1",
                "usage": "internal",
                "location_id": cls.location_src.id,
            }
        )
        cls.location2 = cls.location_model.create(
            {
                "name": "Location 2",
                "usage": "internal",
                "location_id": cls.location_src.id,
            }
        )
        cls.location3 = cls.location_model.create(
            {
                "name": "Location 3",
                "usage": "internal",
                "location_id": cls.location_src.id,
            }
        )
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.quant1 = cls.quant_model.sudo().create(
            {
                "product_id": cls.product.id,
                "quantity": 100.0,
                "location_id": cls.location1.id,
            }
        )
        cls.quant2 = cls.quant_model.sudo().create(
            {
                "product_id": cls.product.id,
                "quantity": 100.0,
                "location_id": cls.location2.id,
            }
        )
        cls.quant3 = cls.quant_model.sudo().create(
            {
                "product_id": cls.product.id,
                "quantity": 100.0,
                "location_id": cls.location3.id,
            }
        )
        cls.move = cls.move_model.create(
            {
                "name": cls.product.name,
                "product_id": cls.product.id,
                "product_uom_qty": 400.0,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.location_src.id,
                "location_dest_id": cls.location_dst.id,
                "picking_type_id": cls.picking_type.id,
            }
        )
        cls.move._action_confirm()

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
