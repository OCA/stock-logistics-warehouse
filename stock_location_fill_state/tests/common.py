# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class LocationFillStateCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.suppliers = cls.env.ref("stock.stock_location_suppliers")
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.stock_1 = cls.env["stock.location"].create(
            {
                "name": "Stock 1",
                "location_id": cls.stock.id,
            }
        )
        cls.stock_2 = cls.env["stock.location"].create(
            {
                "name": "Stock 2",
                "location_id": cls.stock.id,
                "exclude_from_fill_state_computation": True,
            }
        )
