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
        days_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        cls.working_hours_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Working Hours (Mon-Fri, 8-12 + 13-17)",
                "tz": "UTC",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": days_names[day],
                            "dayofweek": str(day),
                            "hour_from": hour,
                            "hour_to": hour + 4,
                            "day_period": "morning" if hour < 12 else "afternoon",
                        },
                    )
                    for day in (0, 1, 2, 3, 4)
                    for hour in (8, 13)
                ],
            }
        )
        cls.reordering_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Reordering Hours (Wed 8-12 + 13-17, Sat 13-17)",
                "tz": "UTC",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": days_names[day],
                            "dayofweek": str(day),
                            "hour_from": hour,
                            "hour_to": hour + 4,
                            "day_period": "morning" if hour < 12 else "afternoon",
                        },
                    )
                    for day, hour in ((2, 8), (2, 13), (5, 13))
                ],
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
        # We want only 1 reordering rule of type "pull" to avoid inconsistent behaviors
        cls.reordering_rule = cls.orderpoint.rule_ids[0]
        cls.reordering_rule.action = "pull"
        other_rules = cls.orderpoint.rule_ids - cls.reordering_rule
        if other_rules:
            other_rules.unlink()
