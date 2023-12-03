from .common import ReserveRuleCommon


class TestReserveRuleFullLot(ReserveRuleCommon):
    @classmethod
    def setUpClass(cls):
        super(TestReserveRuleFullLot, cls).setUpClass()
        cls.rounded = 0.01
        cls.rule_vals = {
            "picking_type_ids": [(6, 0, cls.wh.out_type_id.ids)],
            "sequence": 1,
        }
        cls.no_tolerance_removal_vals = {
            "location_id": cls.loc_zone4.id,
            "removal_strategy": "full_lot",
            "tolerance_requested_limit": "no_tolerance",
            "tolerance_requested_computation": "percentage",
            "tolerance_requested_value": 0.0,
        }
        cls.upper_limit_percentage_vals = {
            "location_id": cls.loc_zone4.id,
            "removal_strategy": "full_lot",
            "tolerance_requested_limit": "upper_limit",
            "tolerance_requested_computation": "percentage",
            "tolerance_requested_value": 50.0,
        }
        cls.upper_limit_absolute_vals = {
            "location_id": cls.loc_zone4.id,
            "removal_strategy": "full_lot",
            "tolerance_requested_limit": "upper_limit",
            "tolerance_requested_computation": "absolute",
            "tolerance_requested_value": 7,
        }
        cls.lower_limit_percentage_vals = {
            "location_id": cls.loc_zone4.id,
            "removal_strategy": "full_lot",
            "tolerance_requested_limit": "lower_limit",
            "tolerance_requested_computation": "percentage",
            "tolerance_requested_value": 50.0,
        }
        cls.lower_limit_absolute_vals = {
            "location_id": cls.loc_zone4.id,
            "removal_strategy": "full_lot",
            "tolerance_requested_limit": "lower_limit",
            "tolerance_requested_computation": "absolute",
            "tolerance_requested_value": 7,
        }

    def test_compare_with_tolerance_no_tolerance(self):
        """Test flow that checks 'No tolerance' comparison"""
        removal = self._create_rule(
            self.rule_vals, [self.no_tolerance_removal_vals]
        ).rule_removal_ids

        result = removal._compare_with_tolerance(1, 2, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(2, 1, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(2, 2, self.rounded)
        self.assertTrue(result, "Compare result must be True")

    def test_compare_with_tolerance_upper_limit_percentage(self):
        """Test flow that checks 'Upper Limit' comparison in percentage"""
        removal = self._create_rule(
            self.rule_vals,
            [self.upper_limit_percentage_vals],
        ).rule_removal_ids

        result = removal._compare_with_tolerance(10, 5, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(10, 16, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(10, 10, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(10, 15, self.rounded)
        self.assertTrue(result, "Compare result must be True")

        result = removal._compare_with_tolerance(10, 11, self.rounded)
        self.assertTrue(result, "Compare result must be True")

    def test_compare_with_tolerance_upper_limit_absolute(self):
        """Test flow that checks 'Upper Limit' comparison in absolute value"""
        removal = self._create_rule(
            self.rule_vals,
            [self.upper_limit_absolute_vals],
        ).rule_removal_ids

        result = removal._compare_with_tolerance(10, 5, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(10, 20, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(10, 10, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(10, 17, self.rounded)
        self.assertTrue(result, "Compare result must be True")

        result = removal._compare_with_tolerance(10, 13, self.rounded)
        self.assertTrue(result, "Compare result must be True")

    def test_compare_with_tolerance_lower_limit_percentage(self):
        """Test flow that checks 'Lower Limit' comparison in percentage"""
        removal = self._create_rule(
            self.rule_vals,
            [self.lower_limit_percentage_vals],
        ).rule_removal_ids

        result = removal._compare_with_tolerance(10, 1, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(10, 11, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(10, 10, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(10, 5, self.rounded)
        self.assertTrue(result, "Compare result must be True")

        result = removal._compare_with_tolerance(10, 7, self.rounded)
        self.assertTrue(result, "Compare result must be True")

    def test_compare_with_tolerance_lower_limit_absolute(self):
        """Test flow that checks 'Lower Limit' comparison in absolute value"""
        removal = self._create_rule(
            self.rule_vals,
            [self.lower_limit_absolute_vals],
        ).rule_removal_ids

        result = removal._compare_with_tolerance(10, 2, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(10, 11, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(10, 10, self.rounded)
        self.assertFalse(result, "Compare result must be False")

        result = removal._compare_with_tolerance(10, 3, self.rounded)
        self.assertTrue(result, "Compare result must be True")

        result = removal._compare_with_tolerance(10, 7, self.rounded)
        self.assertTrue(result, "Compare result must be True")

    def test_compute_tolerance_display(self):
        rule = self._create_rule(
            self.rule_vals,
            [
                self.no_tolerance_removal_vals,
                self.upper_limit_percentage_vals,
                self.upper_limit_absolute_vals,
                self.lower_limit_percentage_vals,
                self.lower_limit_absolute_vals,
            ],
        )
        (
            no_tolerance,
            upper_percentage,
            upper_absolute,
            lower_percentage,
            lower_absolute,
        ) = rule.rule_removal_ids
        self.assertEqual(
            no_tolerance.tolerance_display,
            "Requested Qty = Lot Qty",
            "Tolerance Display must be equal to 'Requested Qty = Lot Qty'",
        )
        self.assertEqual(
            upper_percentage.tolerance_display,
            "Upper Limit (50.0%)",
            "Tolerance Display must be equal to 'Upper Limit (50.0%)'",
        )
        self.assertEqual(
            upper_absolute.tolerance_display,
            "Upper Limit (7.0)",
            "Tolerance Display must be equal to 'Upper Limit (7.0)'",
        )
        self.assertEqual(
            lower_percentage.tolerance_display,
            "Lower Limit (-50.0%)",
            "Tolerance Display must be equal to 'Lower Limit (-50.0%)'",
        )
        self.assertEqual(
            lower_absolute.tolerance_display,
            "Lower Limit (-7.0)",
            "Tolerance Display must be equal to 'Lower Limit (-7.0)'",
        )
