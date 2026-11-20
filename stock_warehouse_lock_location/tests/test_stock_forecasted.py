# Copyright 2026 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo.fields import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockForecastedLockLocation(TransactionCase):
    """Goods in the lock location are left out of the forecast."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product = cls.env["product.product"].create(
            {"name": "Locked Widget", "type": "consu", "is_storable": True}
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

    def _create_delivery(self, qty):
        """Confirm a delivery of `qty` units from the warehouse stock."""
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.out_type_id.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.customer_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "location_dest_id": self.customer_location.id,
                        }
                    )
                ],
            }
        )
        picking.action_confirm()
        return picking

    def test_lock_stock_not_available(self):
        """Goods in the lock location do not make a delivery available.

        Scenario:
            1. Put 10 units in the lock location only.
            2. Confirm a delivery of 5 units.
        Expected:
            - The delivery waits and shows as not available.
        """
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.warehouse.wh_lock_stock_loc_id, 10
        )
        picking = self._create_delivery(5)
        self.assertEqual(picking.state, "confirmed")
        self.assertEqual(picking.move_ids.forecast_availability, -5)
        self.assertEqual(picking.products_availability_state, "late")

    def test_lock_sublocation_stock_not_available(self):
        """Goods in a sub-location of the lock location do not count either.

        Scenario:
            1. Put 10 units in a sub-location of the lock location only.
            2. Confirm a delivery of 5 units.
        Expected:
            - The delivery waits and shows as not available.
        """
        shelf = self.env["stock.location"].create(
            {
                "name": "Shelf A",
                "usage": "internal",
                "location_id": self.warehouse.wh_lock_stock_loc_id.id,
            }
        )
        self.env["stock.quant"]._update_available_quantity(self.product, shelf, 10)
        picking = self._create_delivery(5)
        self.assertEqual(picking.state, "confirmed")
        self.assertEqual(picking.move_ids.forecast_availability, -5)
        self.assertEqual(picking.products_availability_state, "late")

    def test_stock_available(self):
        """Goods in the stock location still make a delivery available.

        Scenario:
            1. Put 10 units in the stock location and 10 in the lock location.
            2. Confirm a delivery of 5 units.
        Expected:
            - The delivery shows as available.
        """
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.warehouse.lot_stock_id, 10
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.warehouse.wh_lock_stock_loc_id, 10
        )
        picking = self._create_delivery(5)
        self.assertEqual(picking.products_availability_state, "available")
