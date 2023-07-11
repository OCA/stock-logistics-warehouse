# © 2023 FactorLibre - Hugo Córdoba <hugo.cordoba@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestReserveExtraPickingCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Bernard Perdant"})
        cls.product = cls.env["product.product"].create({"name": "Product 1"})
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 6.7,
                            "discount": 0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 6.7,
                            "discount": 0,
                        }
                    ),
                ],
            }
        )
        cls.sale_order_2 = cls.sale_order.copy()
