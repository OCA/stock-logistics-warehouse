# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from freezegun import freeze_time

from .common import CommonCalendarOrderpoint


class TestCalendarOrderpoint(CommonCalendarOrderpoint):
    """Lead date of orderpoints are computed from Wednesday."""

    def setUp(self):
        super().setUp()
        # Reset cached value as it could have been computed during initialization
        self.op_model = self.env["stock.warehouse.orderpoint"]
        self.op_model.invalidate_cache(["lead_days_date"])

    @freeze_time("2022-05-30 12:00")  # Monday
    def test_calendar_orderpoint_monday(self):
        # Monday -> Wednesday + 2 days rule delay => Friday
        self.assertEqual(str(self.orderpoint.lead_days_date), "2022-06-03")

    @freeze_time("2022-06-01 12:00")  # Wednesday during working hours
    def test_calendar_orderpoint_wednesday_during_working_hours(self):
        self.op_model.invalidate_cache(["lead_days_date"])  # Recompute field
        self.assertEqual(str(self.orderpoint.lead_days_date), "2022-06-03")

    @freeze_time("2022-06-01 20:00")  # Wednesday after working hours
    def test_calendar_orderpoint_wednesday_outside_working_hours(self):
        self.op_model.invalidate_cache(["lead_days_date"])  # Recompute field
        self.assertEqual(
            str(self.orderpoint.lead_days_date),
            "2022-06-06",  # Postponed to the next working day
        )

    @freeze_time("2022-06-01 23:30")
    def test_calendar_orderpoint_wednesday_outside_of_all_calendars(self):
        # Wednesday outside working hours
        # + outside of reordering timeslots (00:00 -> 23:00)
        self.op_model.invalidate_cache(["lead_days_date"])  # Recompute field
        self.assertEqual(str(self.orderpoint.lead_days_date), "2022-06-10")

    @freeze_time("2022-06-02 11:00")  # Thursday
    def test_calendar_orderpoint_thursday(self):
        self.op_model.invalidate_cache(["lead_days_date"])
        self.assertEqual(str(self.orderpoint.lead_days_date), "2022-06-10")

    @freeze_time("2022-06-09 10:00")  # Next Thursday
    def test_calendar_orderpoint_next_thursday(self):
        self.op_model.invalidate_cache(["lead_days_date"])
        self.assertEqual(str(self.orderpoint.lead_days_date), "2022-06-17")

    @freeze_time("2022-06-01 12:00")  # Wednesday during working hours
    def test_calendar_orderpoint_policy(self):
        self.orderpoint.rule_ids.delay = 4
        # 4 days are counted from Wednesday to Sunday => end on Monday
        self.wh.orderpoint_on_workday_policy = "skip_to_first_workday"
        self.op_model.invalidate_cache(["lead_days_date"])
        self.assertEqual(str(self.orderpoint.lead_days_date), "2022-06-06")
        # 4 days are counted from Wednesday, skipping the weekend => end on Tuesday
        self.wh.orderpoint_on_workday_policy = "skip_all_non_workdays"
        self.op_model.invalidate_cache(["lead_days_date"])
        self.assertEqual(str(self.orderpoint.lead_days_date), "2022-06-07")
