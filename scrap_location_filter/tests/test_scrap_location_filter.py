# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class StockScrapLocation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(StockScrapLocation, cls).setUpClass()

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.ProductObj = cls.env["product.product"]
        cls.LotObj = cls.env["stock.production.lot"]
        cls.productA = cls.ProductObj.create({"name": "Product A", "type": "product"})
        cls.productB = cls.ProductObj.create({"name": "Product B", "type": "product"})
        cls.lot_productA = cls.LotObj.create(
            {
                "name": "A Lot 1",
                "product_id": cls.productA.id,
                "company_id": cls.env.company.id,
            }
        )

    def test_scrap_location(self):
        self.env["stock.quant"].create(
            {
                "product_id": self.productA.id,
                "lot_id": self.lot_productA.id,
                "location_id": self.stock_location.id,
                "inventory_quantity": 100,
            }
        )
        self.env["stock.location"].with_context(
            {"product_id": self.productA.id, "lot_id": self.lot_productA.id}
        ).search([])

    def test_scrap_location2(self):
        self.env["stock.quant"].create(
            {
                "product_id": self.productB.id,
                "lot_id": self.lot_productA.id,
                "location_id": self.stock_location.id,
                "inventory_quantity": 100,
            }
        )
        self.env["stock.location"].with_context(
            {"product_id": self.productA.id, "lot_id": self.lot_productA.id}
        ).search([])
        scrap = self.env["stock.scrap"].create(
            {
                "product_id": self.productA.id,
                "product_uom_id": self.productA.uom_id.id,
                "scrap_qty": 5,
                # "picking_id": picking.id,
                # "reason_code_id": self.reason_code.id,
            }
        )
        scrap._onchange_product_id()
        scrap._onchange_lot_id()
