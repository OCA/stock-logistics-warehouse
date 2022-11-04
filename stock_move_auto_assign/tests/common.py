# Copyright 2020-2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase


class StockMoveAutoAssignCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.wh = cls.env.ref("stock.warehouse0")
        cls.out_type = cls.wh.out_type_id
        cls.in_type = cls.wh.in_type_id
        cls.int_type = cls.wh.int_type_id

        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.supplier_loc = cls.env.ref("stock.stock_location_suppliers")
        cls.shelf1_loc = cls.env.ref("stock.stock_location_components")
        cls.shelf2_loc = cls.env.ref("stock.stock_location_14")

        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )

    def _create_move(
        self,
        product,
        picking_type,
        qty=1.0,
        state="confirmed",
        procure_method="make_to_stock",
        move_dest=None,
    ):
        source = picking_type.default_location_src_id or self.supplier_loc
        dest = picking_type.default_location_dest_id or self.customer_loc
        move_vals = {
            "name": product.name,
            "product_id": product.id,
            "product_uom_qty": qty,
            "product_uom": product.uom_id.id,
            "picking_type_id": picking_type.id,
            "location_id": source.id,
            "location_dest_id": dest.id,
            "state": state,
            "procure_method": procure_method,
        }
        if move_dest:
            move_vals["move_dest_ids"] = [(4, move_dest.id, False)]
        return self.env["stock.move"].create(move_vals)

    def _update_qty_in_location(self, location, product, quantity):
        location.env["stock.quant"]._update_available_quantity(
            product, location, quantity
        )
