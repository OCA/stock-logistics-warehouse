# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class StockLocationLockdownCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Location = cls.env["stock.location"]
        cls.Quant = cls.env["stock.quant"]
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product lockdown",
                "type": "consu",
                "is_storable": True,
                "tracking": "none",
            }
        )
        cls.free_location = cls.Location.create(
            {
                "name": "free",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )

    def _create_move(self, source, dest, qty):
        return self.env["stock.move"].create(
            {
                "location_id": source.id,
                "location_dest_id": dest.id,
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "quantity": qty,
                "picked": True,
                "product_uom": self.product.uom_id.id,
                "name": "test move",
                "move_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_id": self.product.uom_id.id,
                            "quantity": qty,
                            "location_id": source.id,
                            "location_dest_id": dest.id,
                        },
                    )
                ],
            }
        )
