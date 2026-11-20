# Copyright 2026 Camptocamp SA
# @author Hadrien Huvelle <hadrien.huvelle@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


# After every module is loaded: the tests create records of models that other
# installed modules extend (e.g. required columns on partners).
@tagged("post_install", "-at_install")
class InventoryReportCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                **DISABLED_MAIL_CONTEXT,
            )
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.external_inventory_user_id = cls.env.user

        cls.product = cls.env["product.product"].create(
            {
                "name": "Inventory Product",
                "default_code": "INV-001",
                "type": "consu",
                "is_storable": True,
                "standard_price": 12.5,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Inventory Product 2",
                "default_code": "INV-002",
                "type": "consu",
                "is_storable": True,
                "standard_price": 0.0,
            }
        )
        cls.product_lot = cls.env["product.product"].create(
            {
                "name": "Inventory Product Lot",
                "default_code": "INV-LOT-001",
                "type": "consu",
                "is_storable": True,
                "tracking": "lot",
                "standard_price": 5.0,
            }
        )

    @classmethod
    def _create_report(cls, **vals):
        """Create a report of the test warehouse."""
        return cls.env["stock.external.inventory.report"].create(
            dict({"warehouse_id": cls.warehouse.id}, **vals)
        )

    @classmethod
    def _activities_for_report(cls, report):
        return cls.env["mail.activity"].search(
            [
                ("res_model", "=", "stock.external.inventory.report"),
                ("res_id", "=", report.id),
            ]
        )
