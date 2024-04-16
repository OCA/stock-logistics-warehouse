# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.tests.common import SavepointCase


class CommonCalendarOrderpoint(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env.ref("product.product_delivery_02").copy()
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.wh.write(
            {
                "calendar_id": cls.env.ref("resource.resource_calendar_std").id,
                "orderpoint_calendar_id": cls.env.ref(
                    "stock_warehouse_calendar_orderpoint.resource_calendar_orderpoint_demo"
                ).id,
                "orderpoint_on_workday": True,
                "orderpoint_on_workday_policy": "skip_to_first_workday",
            }
        )
        cls.orderpoint = cls.env["stock.warehouse.orderpoint"].create(
            {
                "warehouse_id": cls.wh.id,
                "location_id": cls.wh.lot_stock_id.id,
                "product_id": cls.product.id,
                "product_min_qty": "10",
                "product_max_qty": "20",
                "product_uom": cls.env.ref("uom.product_uom_unit"),
            }
        )
        cls.orderpoint.rule_ids.write({"action": "pull", "delay": 2})
