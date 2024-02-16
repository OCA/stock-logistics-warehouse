# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import TransactionCase


class TestCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.location_dest = cls.env["stock.location"].create(
            {
                "name": "Test dest location",
                "usage": cls.env.ref("stock.stock_location_stock").usage,
            }
        )
        cls.meter_uom = cls.env.ref("uom.product_uom_meter")
        cls.cm_uom = cls.env.ref("uom.product_uom_cm")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "uom_id": cls.cm_uom.id,
                "uom_po_id": cls.meter_uom.id,
            }
        )
        cls.stock_picking_type = cls.env["stock.picking.type"].create(
            {
                "name": "Internal transfer",
                "code": "internal",
                "sequence_code": "INT",
            }
        )
        cls.stock_move = cls.env["stock.move"].create(
            {
                "name": cls.product.display_name,
                "location_id": cls.location.id,
                "location_dest_id": cls.location_dest.id,
                "product_id": cls.product.id,
                "product_uom_qty": 1,
                "picking_type_id": cls.stock_picking_type.id,
                "product_uom": cls.cm_uom.id,
            }
        )
