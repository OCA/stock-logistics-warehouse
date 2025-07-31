# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class DefaultPutawayCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockLocation = cls.env["stock.location"]
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.stock_1 = cls.StockLocation.create(
            {
                "name": "Stock 1",
                "location_id": cls.stock.id,
            }
        )
        cls.stock_2 = cls.StockLocation.create(
            {
                "name": "Stock 2",
                "location_id": cls.stock.id,
            }
        )
        cls.warehouse_2 = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 2",
                "code": "WH2",
            }
        )
        cls.stock_wh2 = cls.warehouse_2.lot_stock_id
        cls.stock_wh2_3 = cls.StockLocation.create(
            {"name": "Stock 3", "location_id": cls.stock_wh2.id}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "putaway_rule_ids": [
                    Command.create(
                        {
                            "location_in_id": cls.stock.id,
                            "location_out_id": cls.stock_1.id,
                        }
                    ),
                    Command.create(
                        {
                            "location_in_id": cls.stock_wh2.id,
                            "location_out_id": cls.stock_wh2_3.id,
                        }
                    ),
                ],
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "putaway_rule_ids": [
                    Command.create(
                        {
                            "location_in_id": cls.stock.id,
                            "location_out_id": cls.stock_1.id,
                        }
                    ),
                ],
            }
        )
