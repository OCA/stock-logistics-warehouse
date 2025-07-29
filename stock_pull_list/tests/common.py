# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta as td

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestPullListCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wh_obj = cls.env["stock.warehouse"]
        cls.move_obj = cls.env["stock.move"]
        cls.picking_obj = cls.env["stock.picking"]
        cls.wiz_obj = cls.env["stock.pull.list.wizard"]
        cls.stock_change_obj = cls.env["stock.change.product.qty"]

        cls.company = cls.env.ref("base.main_company")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")

        cls.warehouse_2 = cls.wh_obj.create({"code": "WH-T", "name": "Warehouse Test"})
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "test product A",
                "default_code": "TEST-A",
                "is_storable": True,
            }
        )

        route_vals = {
            "name": "WH2 -> WH",
        }
        cls.transfer_route = cls.env["stock.route"].create(route_vals)
        rule_vals = {
            "location_src_id": cls.warehouse_2.lot_stock_id.id,
            "location_dest_id": cls.warehouse.lot_stock_id.id,
            "action": "pull_push",
            "warehouse_id": cls.warehouse.id,
            "propagate_warehouse_id": cls.warehouse_2.id,
            "picking_type_id": cls.env.ref("stock.picking_type_internal").id,
            "name": "WH2->WH",
            "route_id": cls.transfer_route.id,
            "delay": 1,
        }
        cls.transfer_rule = cls.env["stock.rule"].create(rule_vals)
        cls.product_a.route_ids = [Command.set(cls.transfer_route.ids)]

        # Dates:
        cls.today = fields.Datetime.today()
        cls.yesterday = cls.today - td(days=1)
        cls.date_3 = cls.today + td(days=3)

    @classmethod
    def _generate_moves(cls):
        cls.create_picking_out_a(cls.yesterday, 50)
        cls.create_picking_out_a(cls.date_3, 70)

    @classmethod
    def create_picking_out_a(cls, date_move, qty):
        picking = cls.picking_obj.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "location_dest_id": cls.customer_loc.id,
                "scheduled_date": date_move,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Test move",
                            "product_id": cls.product_a.id,
                            "date": date_move,
                            "product_uom": cls.product_a.uom_id.id,
                            "product_uom_qty": qty,
                            "location_id": cls.warehouse.lot_stock_id.id,
                            "location_dest_id": cls.customer_loc.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        return picking

    @classmethod
    def _update_product_qty(cls, product, quantity):
        """Update Product quantity."""
        change_product_qty = cls.stock_change_obj.create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": quantity,
            }
        )
        change_product_qty.change_product_qty()
        return change_product_qty
