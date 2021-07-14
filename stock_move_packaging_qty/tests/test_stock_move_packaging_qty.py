# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import SavepointCase


class TestStockMovePackagingQty(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "Test packaging", "product_id": cls.product.id, "qty": 5.0}
        )
        cls.wh = cls.env["stock.warehouse"].create({
            "name": "Base Warehouse",
            "code": "TESTWH"
        })
        cls.categ_unit = cls.env.ref("uom.product_uom_categ_unit")
        cls.uom_unit = cls.env["uom.uom"].search(
            [
                ("category_id", "=", cls.categ_unit.id),
                ("uom_type", "=", "reference")
            ],
            limit=1
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")

    def test_product_packaging_qty(self):
        move = self.env["stock.move"].create({
            "name": "Move",
            "location_id": self.supplier_location.id,
            "location_dest_id": self.wh.lot_stock_id.id,
            "partner_id": self.partner.id,
            "product_id": self.product.id,
            "product_uom": self.product.uom_id.id,
            "product_uom_qty": 3.0,
            "price_unit": 10.0,
        })
        move.write({"product_packaging": self.packaging.id})
        move._onchange_product_packaging()
        self.assertEqual(move.product_uom_qty, 5.0)
        self.assertEqual(move.product_packaging_qty, 1.0)
        move.write({"product_packaging_qty": 3.0})
        self.assertEqual(move.product_uom_qty, 15.0)
