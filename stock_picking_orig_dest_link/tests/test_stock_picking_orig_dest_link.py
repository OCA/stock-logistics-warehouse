# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestPickingOrigDestLink(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Models
        cls.product_model = cls.env["product.product"]
        cls.picking_model = cls.env["stock.picking"]
        cls.partner_model = cls.env["res.partner"]
        cls.move_model = cls.env["stock.move"]

        # Created records
        cls.product = cls.product_model.create({"name": "Test Product"})
        cls.partner = cls.partner_model.create({"name": "Test Partner"})

        # Data records
        cls.pick_type_in = cls.env.ref("stock.picking_type_in")
        cls.pick_type_out = cls.env.ref("stock.picking_type_out")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.suppliers_location = cls.env.ref("stock.stock_location_suppliers")

    @classmethod
    def _create_in_picking(cls):
        picking = cls.picking_model.create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.pick_type_in.id,
                "location_id": cls.suppliers_location.id,
                "location_dest_id": cls.stock_location.id,
            }
        )
        move_vals = {
            "picking_id": picking.id,
            "product_id": cls.product.id,
            "location_dest_id": cls.stock_location.id,
            "location_id": cls.suppliers_location.id,
            "name": cls.product.name,
            "product_uom_qty": 1,
            "product_uom": cls.product.uom_id.id,
        }
        cls.move_model.create(move_vals)
        return picking

    @classmethod
    def _create_out_picking(cls):
        picking = cls.picking_model.create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.pick_type_out.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customers_location.id,
            }
        )
        move_vals = {
            "picking_id": picking.id,
            "product_id": cls.product.id,
            "location_id": cls.stock_location.id,
            "location_dest_id": cls.customers_location.id,
            "name": cls.product.name,
            "product_uom_qty": 1,
            "product_uom": cls.product.uom_id.id,
        }
        cls.move_model.create(move_vals)
        return picking

    @classmethod
    def _link_moves_from_pickings(cls, in_picking, out_picking):
        in_move_ids = in_picking.move_lines
        out_move_ids = out_picking.move_lines
        return in_move_ids.write({"move_dest_ids": out_move_ids})

    def test_01_in_out_pickings(self):
        # create in and out picking and links their moves
        in_pick = self._create_in_picking()
        out_pick = self._create_out_picking()
        result = self._link_moves_from_pickings(in_pick, out_pick)
        self.assertTrue(result)
        # check that pickings have also been linked
        self.assertEqual(in_pick.dest_picking_ids, out_pick)
        self.assertEqual(out_pick.orig_picking_ids, in_pick)
