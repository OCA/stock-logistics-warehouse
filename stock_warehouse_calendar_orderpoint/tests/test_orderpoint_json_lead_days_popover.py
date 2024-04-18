# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from json import loads

from freezegun import freeze_time

from .common import CommonCalendarOrderpoint


class TestOrderpointJsonPopover(CommonCalendarOrderpoint):
    """Tests orderpoint's Json popover info"""

    @freeze_time("2024-04-01 10:00")
    def test_00_json_popover_info(self):
        self.wh.orderpoint_calendar_id = self.reordering_calendar
        self.wh.calendar_id = self.working_hours_calendar
        self.reordering_rule.delay = 5
        self.env["stock.warehouse.orderpoint"].invalidate_cache(
            ["json_lead_days_popover"]
        )
        info = loads(self.orderpoint.json_lead_days_popover)
        self.assertIn("lead_days_description", info)
        self.assertIn(
            "<td>Reordering Date</td><td class='text-right'>04/03/2024</td>",
            info["lead_days_description"],
        )
