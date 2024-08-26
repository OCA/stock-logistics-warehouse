# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from freezegun import freeze_time

from .common import CommonCalendarOrderpoint


class TestOrderpointLeadDaysDate(CommonCalendarOrderpoint):
    """Tests orderpoints' forecast date computations

    The OP calendar defines reordering slots as Wed 8-12 + 13-17, Sat 13-17.
    The WH calendar defines workdays as Mon-Fri 8-12 + 13-17.

    Each test is determined by the date it's executed on, and whether the OP calendar
    is set or not. Tests are executed on:
        - Monday (non-reordering day for OP calendar, workday for WH calendar)
        - Wednesday (reordering day for OP calendar, workday for WH calendar)
        - Saturday (reordering day for OP calendar, non-workday for WH calendar)
        - Sunday (non-reordering day for OP calendar, non-workday for WH calendar)
    On Wednesday and Saturday, tests are executed before, during, after and between
    reordering slots.

    In each test, the forecast date is tested 5 times:
        - 1: WH calendar set, lead days ≠ 0, policy = "skip_to_first_workday"
        - 2: WH calendar set, lead days ≠ 0, policy = "skip_all_non_workdays"
        - 3: WH calendar not set, lead days ≠ 0
        - 4: WH calendar set, lead days = 0
        - 5: WH calendar not set, lead days ≠ 0
    """

    def _test_with_values(self, op_calendar, wh_calendar, policy, delay, expected_dt):
        self.wh.orderpoint_calendar_id = op_calendar
        self.wh.calendar_id = wh_calendar
        self.wh.orderpoint_on_workday_policy = policy
        self.reordering_rule.delay = delay
        self.env["stock.warehouse.orderpoint"].invalidate_cache(["lead_days_date"])
        self.assertEqual(str(self.orderpoint.lead_days_date), expected_dt)

    @freeze_time("2024-04-01 10:00")
    def test_00_monday_with_orderpoint_calendar_set(self):
        self.wh.orderpoint_calendar_id = self.reordering_calendar
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-03 08:00:00"
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_to_first_workday",
            4,
            "2024-04-08",
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_all_non_workdays",
            4,
            "2024-04-09",
        )
        self._test_with_values(self.reordering_calendar, False, False, 4, "2024-04-07")
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            False,
            0,
            "2024-04-03",
        )
        self._test_with_values(self.reordering_calendar, False, False, 0, "2024-04-03")

    @freeze_time("2024-04-01 12:00")
    def test_01_monday_with_orderpoint_calendar_unset(self):
        self.wh.orderpoint_calendar_id = False
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-01 12:00:00"
        )
        self._test_with_values(
            False, self.working_hours_calendar, "skip_to_first_workday", 6, "2024-04-08"
        )
        self._test_with_values(
            False, self.working_hours_calendar, "skip_all_non_workdays", 6, "2024-04-09"
        )
        self._test_with_values(False, False, False, 6, "2024-04-07")
        self._test_with_values(
            False, self.working_hours_calendar, False, 0, "2024-04-01"
        )
        self._test_with_values(False, False, False, 0, "2024-04-01")

    @freeze_time("2024-04-03 06:00")
    def test_02_wednesday_with_orderpoint_calendar_set_before_first_slot(self):
        self.wh.orderpoint_calendar_id = self.reordering_calendar
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-03 08:00:00"
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_to_first_workday",
            4,
            "2024-04-08",
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_all_non_workdays",
            4,
            "2024-04-09",
        )
        self._test_with_values(self.reordering_calendar, False, False, 4, "2024-04-07")
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            False,
            0,
            "2024-04-03",
        )
        self._test_with_values(self.reordering_calendar, False, False, 0, "2024-04-03")

    @freeze_time("2024-04-03 10:00")
    def test_03_wednesday_with_orderpoint_calendar_set_during_first_slot(self):
        self.wh.orderpoint_calendar_id = self.reordering_calendar
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-03 10:00:00"
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_to_first_workday",
            4,
            "2024-04-08",
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_all_non_workdays",
            4,
            "2024-04-09",
        )
        self._test_with_values(self.reordering_calendar, False, False, 4, "2024-04-07")
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            False,
            0,
            "2024-04-03",
        )
        self._test_with_values(self.reordering_calendar, False, False, 0, "2024-04-03")

    @freeze_time("2024-04-03 12:30")
    def test_04_wednesday_with_orderpoint_calendar_set_between_slots(self):
        self.wh.orderpoint_calendar_id = self.reordering_calendar
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-03 13:00:00"
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_to_first_workday",
            4,
            "2024-04-08",
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_all_non_workdays",
            4,
            "2024-04-09",
        )
        self._test_with_values(self.reordering_calendar, False, False, 4, "2024-04-07")
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            False,
            0,
            "2024-04-03",
        )
        self._test_with_values(self.reordering_calendar, False, False, 0, "2024-04-03")

    @freeze_time("2024-04-03 15:00")
    def test_05_wednesday_with_orderpoint_calendar_set_during_second_slot(self):
        self.wh.orderpoint_calendar_id = self.reordering_calendar
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-03 15:00:00"
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_to_first_workday",
            4,
            "2024-04-08",
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_all_non_workdays",
            4,
            "2024-04-09",
        )
        self._test_with_values(self.reordering_calendar, False, False, 4, "2024-04-07")
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            False,
            0,
            "2024-04-03",
        )
        self._test_with_values(self.reordering_calendar, False, False, 0, "2024-04-03")

    @freeze_time("2024-04-03 19:00")
    def test_06_wednesday_with_orderpoint_calendar_set_after_second_slot(self):
        self.wh.orderpoint_calendar_id = self.reordering_calendar
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-06 13:00:00"
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_to_first_workday",
            7,
            "2024-04-15",
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_all_non_workdays",
            7,
            "2024-04-16",
        )
        self._test_with_values(self.reordering_calendar, False, False, 4, "2024-04-10")
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            False,
            0,
            "2024-04-08",
        )
        self._test_with_values(self.reordering_calendar, False, False, 0, "2024-04-06")

    @freeze_time("2024-04-03 12:00")
    def test_07_wednesday_with_orderpoint_calendar_unset(self):
        self.wh.orderpoint_calendar_id = False
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-03 12:00:00"
        )
        self._test_with_values(
            False, self.working_hours_calendar, "skip_to_first_workday", 4, "2024-04-08"
        )
        self._test_with_values(
            False, self.working_hours_calendar, "skip_all_non_workdays", 4, "2024-04-09"
        )
        self._test_with_values(False, False, False, 4, "2024-04-07")
        self._test_with_values(
            False, self.working_hours_calendar, False, 0, "2024-04-03"
        )
        self._test_with_values(False, False, False, 0, "2024-04-03")

    @freeze_time("2024-04-06 12:00")
    def test_08_saturday_with_orderpoint_calendar_set_before_slot(self):
        self.wh.orderpoint_calendar_id = self.reordering_calendar
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-06 13:00:00"
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_to_first_workday",
            2,
            "2024-04-08",
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_all_non_workdays",
            2,
            "2024-04-09",
        )
        self._test_with_values(self.reordering_calendar, False, False, 7, "2024-04-13")
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            False,
            0,
            "2024-04-08",
        )
        self._test_with_values(self.reordering_calendar, False, False, 0, "2024-04-06")

    @freeze_time("2024-04-06 15:00")
    def test_09_saturday_with_orderpoint_calendar_set_during_slot(self):
        self.wh.orderpoint_calendar_id = self.reordering_calendar
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-06 15:00:00"
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_to_first_workday",
            2,
            "2024-04-08",
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_all_non_workdays",
            2,
            "2024-04-09",
        )
        self._test_with_values(self.reordering_calendar, False, False, 7, "2024-04-13")
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            False,
            0,
            "2024-04-08",
        )
        self._test_with_values(self.reordering_calendar, False, False, 0, "2024-04-06")

    @freeze_time("2024-04-06 18:00")
    def test_10_saturday_with_orderpoint_calendar_set_after_slot(self):
        self.wh.orderpoint_calendar_id = self.reordering_calendar
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-10 08:00:00"
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_to_first_workday",
            4,
            "2024-04-15",
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_all_non_workdays",
            4,
            "2024-04-16",
        )
        self._test_with_values(self.reordering_calendar, False, False, 4, "2024-04-14")
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            False,
            0,
            "2024-04-10",
        )
        self._test_with_values(self.reordering_calendar, False, False, 0, "2024-04-10")

    @freeze_time("2024-04-06 12:00")
    def test_11_saturday_with_orderpoint_calendar_unset(self):
        self.wh.orderpoint_calendar_id = False
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-06 12:00:00"
        )
        self._test_with_values(
            False, self.working_hours_calendar, "skip_to_first_workday", 7, "2024-04-15"
        )
        self._test_with_values(
            False, self.working_hours_calendar, "skip_all_non_workdays", 7, "2024-04-16"
        )
        self._test_with_values(False, False, False, 4, "2024-04-10")
        self._test_with_values(
            False, self.working_hours_calendar, False, 0, "2024-04-08"
        )
        self._test_with_values(False, False, False, 0, "2024-04-06")

    @freeze_time("2024-04-07 12:00")
    def test_12_sunday_with_orderpoint_calendar_set(self):
        self.wh.orderpoint_calendar_id = self.reordering_calendar
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-10 08:00:00"
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_to_first_workday",
            4,
            "2024-04-15",
        )
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            "skip_all_non_workdays",
            4,
            "2024-04-16",
        )
        self._test_with_values(self.reordering_calendar, False, False, 4, "2024-04-14")
        self._test_with_values(
            self.reordering_calendar,
            self.working_hours_calendar,
            False,
            0,
            "2024-04-10",
        )
        self._test_with_values(self.reordering_calendar, False, False, 0, "2024-04-10")

    @freeze_time("2024-04-07 12:00")
    def test_13_sunday_with_orderpoint_calendar_unset(self):
        self.wh.orderpoint_calendar_id = False
        self.assertEqual(
            str(self.orderpoint._get_next_reordering_date()), "2024-04-07 12:00:00"
        )
        self._test_with_values(
            False, self.working_hours_calendar, "skip_to_first_workday", 7, "2024-04-15"
        )
        self._test_with_values(
            False, self.working_hours_calendar, "skip_all_non_workdays", 7, "2024-04-16"
        )
        self._test_with_values(False, False, False, 7, "2024-04-14")
        self._test_with_values(
            False, self.working_hours_calendar, False, 0, "2024-04-08"
        )
        self._test_with_values(False, False, False, 0, "2024-04-07")
