# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class SaleStockAvailableInfoPopup(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user_group_stock_user = cls.env.ref("stock.group_stock_user")
        cls.user_stock_user = cls.env["res.users"].create(
            {
                "name": "Pauline Poivraisselle",
                "login": "pauline",
                "email": "p.p@example.com",
                "notification_type": "inbox",
                "groups_id": [(6, 0, [user_group_stock_user.id])],
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Storable product", "type": "product"}
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.suppliers_location = cls.env.ref("stock.stock_location_suppliers")
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.stock_location.id,
                "quantity": 40.0,
            }
        )
        cls.picking_out = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customers_location.id,
            }
        )
        cls.env["stock.move"].create(
            {
                "name": "a move",
                "product_id": cls.product.id,
                "product_uom_qty": 3.0,
                "product_uom": cls.product.uom_id.id,
                "picking_id": cls.picking_out.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customers_location.id,
            }
        )
        cls.picking_in = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.suppliers_location.id,
                "location_dest_id": cls.stock_location.id,
            }
        )
        cls.env["stock.move"].create(
            {
                "restrict_partner_id": cls.user_stock_user.partner_id.id,
                "name": "another move",
                "product_id": cls.product.id,
                "product_uom_qty": 5.0,
                "product_uom": cls.product.uom_id.id,
                "picking_id": cls.picking_in.id,
                "location_id": cls.suppliers_location.id,
                "location_dest_id": cls.stock_location.id,
            }
        )

    def test_immediately_usable_qty_today(self):
        self.picking_out.action_confirm()
        self.picking_in.action_assign()
        so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                ],
            }
        )
        line = so.order_line
        self.assertEqual(
            line.immediately_usable_qty_today, self.product.immediately_usable_qty,
        )

    def test_immediately_usable_qty_today_similar_solines(self):
        """Create a sale order containing three times the same product. The
        quantity available should be different for the 3 lines.
        """
        so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "sequence": 2,
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "sequence": 3,
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 5,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(
            so.order_line.mapped("immediately_usable_qty_today"),
            [
                self.product.immediately_usable_qty,
                self.product.immediately_usable_qty - 5,
                self.product.immediately_usable_qty - 10,
            ],
        )
