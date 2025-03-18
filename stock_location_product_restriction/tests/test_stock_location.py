# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form, TransactionCase


class TestStockLocation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.StockLocation = cls.env["stock.location"]
        cls.StockLocation._parent_store_compute()
        cls.loc_lvl = cls.env.ref("stock.stock_location_locations")
        cls.loc_lvl_1 = cls.StockLocation.create(
            {"name": "level_1", "location_id": cls.loc_lvl.id}
        )
        cls.loc_lvl_1_1 = cls.StockLocation.create(
            {"name": "level_1_1", "location_id": cls.loc_lvl_1.id}
        )

        cls.loc_lvl_1_1_1 = cls.StockLocation.create(
            {"name": "level_1_1_1", "location_id": cls.loc_lvl_1_1.id}
        )
        cls.loc_lvl_1_1_2 = cls.StockLocation.create(
            {"name": "level_1_1_1", "location_id": cls.loc_lvl_1_1.id}
        )
        cls.default_product_restriction = "any"

        # products
        Product = cls.env["product.product"]
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product_1 = Product.create(
            {"name": "Wood", "type": "product", "uom_id": cls.uom_unit.id}
        )
        cls.product_2 = Product.create(
            {"name": "Stone", "type": "product", "uom_id": cls.uom_unit.id}
        )

        # quants
        StockQuant = cls.env["stock.quant"]
        cls.quant_1_lvl_1_1_1 = StockQuant.create(
            {
                "product_id": cls.product_1.id,
                "location_id": cls.loc_lvl_1_1_1.id,
                "quantity": 10.0,
                "owner_id": cls.env.user.id,
            }
        )
        cls.quant_2_lvl_1_1_1 = StockQuant.create(
            {
                "product_id": cls.product_2.id,
                "location_id": cls.loc_lvl_1_1_1.id,
                "quantity": 10.0,
                "owner_id": cls.env.user.id,
            }
        )
        cls.quant_1_lvl_1_1_2 = StockQuant.create(
            {
                "product_id": cls.product_1.id,
                "location_id": cls.loc_lvl_1_1_2.id,
                "quantity": 10.0,
                "owner_id": cls.env.user.id,
            }
        )
        cls.quant_2_lvl_1_1_2 = StockQuant.create(
            {
                "product_id": cls.product_2.id,
                "location_id": cls.loc_lvl_1_1_2.id,
                "quantity": 10.0,
                "owner_id": cls.env.user.id,
            }
        )

    def test_00(self):
        """
        Data:
            A 3 depths location hierarchy without
            specific_product_restriction
        Test Case:
            1. Specify a specific_product_restriction at root level
        Expected result:
            The value at each level must modified.
        """
        self.loc_lvl_1.specific_product_restriction = "same"
        children = self.loc_lvl_1.child_ids

        def check_field(locs, name):
            for loc in locs:
                self.assertEqual(
                    name,
                    loc.product_restriction,
                    "Wrong product restriction on loc %s" % loc.name,
                )
                check_field(loc.child_ids, name)

        check_field(children, "same")

    def test_01(self):
        """
        Data:
            A 3 depths location hierarchy without
            specific_product_restriction
        Test Case:
            1. Specify a specific_product_restriction at level_1_1
        Expected result:
            The value at root level and level 1 is the default
            The value at level_1_1 and level_1_1_1 is the new one
        """
        self.loc_lvl_1_1.specific_product_restriction = "same"
        self.loc_lvl_1_1.flush_recordset()
        self.assertEqual(
            self.default_product_restriction,
            self.loc_lvl.product_restriction,
        )
        self.assertEqual(
            self.default_product_restriction,
            self.loc_lvl_1.product_restriction,
        )
        self.assertEqual("same", self.loc_lvl_1_1.product_restriction)
        self.assertEqual("same", self.loc_lvl_1_1_1.product_restriction)

    def test_02(self):
        """
        Data:
            Location level_1_1_1 with 2 different products no restriction
            Location level_1_1_2 with 2 different products no restriction
        Test Case:
            1. Search location child of loc_lvl with restriction violation
            2. Search location child of loc_lvl without restriction violation
        Expected result:
            1. No result
            2. All child location are returned
        """
        self.loc_lvl_1_1_1.product_restriction = "any"
        self.loc_lvl_1_1_2.product_restriction = "any"
        # has violation
        res = self.StockLocation.search(
            [
                ("id", "child_of", self.loc_lvl.id),
                ("has_restriction_violation", "=", True),
            ]
        )
        self.assertFalse(res)
        res = self.StockLocation.search(
            [
                ("id", "child_of", self.loc_lvl.id),
                ("has_restriction_violation", "!=", False),
            ]
        )
        self.assertFalse(res)
        # without violation
        res = self.StockLocation.search(
            [
                ("id", "child_of", self.loc_lvl.id),
                ("has_restriction_violation", "=", False),
            ]
        )
        self.assertIn(self.loc_lvl_1_1_1, res)
        self.assertIn(self.loc_lvl_1_1_2, res)
        res = self.StockLocation.search(
            [
                ("id", "child_of", self.loc_lvl.id),
                ("has_restriction_violation", "!=", True),
            ]
        )
        self.assertIn(self.loc_lvl_1_1_1, res)
        self.assertIn(self.loc_lvl_1_1_2, res)

    def test_03(self):
        """
        Data:
            * Location level_1_1_1 with 2 different products no restriction
            * Location level_1_1_2 with 2 different products
              with restriction same
        Test Case:
            1. Search location child of loc_lvl with restriction violation
            2. Search location child of loc_lvl without restriction violation
            3. Set restriction 'same' on location level_1_1_1
            4. Search location child of loc_lvl with restriction violation
        Expected result:
            1. result = level_1_1_2
            2. level_1_1_2 is not into result but level_1_1_1 is
            4. result = level_1_1_2 and level_1_1_1
        """
        self.loc_lvl_1_1_1.product_restriction = "any"
        self.loc_lvl_1_1_2.product_restriction = "same"
        (self.loc_lvl_1_1_1 | self.loc_lvl_1_1_2).flush_recordset()
        # 1
        res = self.StockLocation.search(
            [
                ("id", "child_of", self.loc_lvl.id),
                ("has_restriction_violation", "=", True),
            ]
        )
        self.assertEqual(self.loc_lvl_1_1_2, res)
        res = self.StockLocation.search(
            [
                ("id", "child_of", self.loc_lvl.id),
                ("has_restriction_violation", "!=", False),
            ]
        )
        self.assertEqual(self.loc_lvl_1_1_2, res)
        # 2
        res = self.StockLocation.search(
            [
                ("id", "child_of", self.loc_lvl.id),
                ("has_restriction_violation", "=", False),
            ]
        )
        self.assertIn(self.loc_lvl_1_1_1, res)
        self.assertNotIn(self.loc_lvl_1_1_2, res)
        res = self.StockLocation.search(
            [
                ("id", "child_of", self.loc_lvl.id),
                ("has_restriction_violation", "!=", True),
            ]
        )
        self.assertIn(self.loc_lvl_1_1_1, res)
        self.assertNotIn(self.loc_lvl_1_1_2, res)
        # 3
        self.loc_lvl_1_1_1.product_restriction = "same"
        self.loc_lvl_1_1_2.product_restriction = "same"
        (self.loc_lvl_1_1_1 | self.loc_lvl_1_1_2).flush_recordset()
        # 4
        res = self.StockLocation.search(
            [
                ("id", "child_of", self.loc_lvl.id),
                ("has_restriction_violation", "=", True),
            ]
        )
        self.assertEqual(self.loc_lvl_1_1_2 | self.loc_lvl_1_1_1, res)
        res = self.StockLocation.search(
            [
                ("id", "child_of", self.loc_lvl.id),
                ("has_restriction_violation", "!=", False),
            ]
        )
        self.assertEqual(self.loc_lvl_1_1_2 | self.loc_lvl_1_1_1, res)

    def test_04(self):
        """
          Data:
            * Location level_1_1_1 with 2 different products no restriction
        Test Case:
            1. Check restriction message
            3. Set restriction 'same' on location level_1_1_1
            4. Check restriction message
        Expected result:
            1. No restriction message
            3. Retriction message
        """
        self.loc_lvl_1_1_1.product_restriction = "any"
        self.loc_lvl_1_1_1.flush_recordset()
        self.assertFalse(self.loc_lvl_1_1_1.has_restriction_violation)
        self.assertFalse(self.loc_lvl_1_1_1.restriction_violation_message)
        self.loc_lvl_1_1_1.product_restriction = "same"
        self.loc_lvl_1_1_1.flush_recordset()
        self.assertTrue(self.loc_lvl_1_1_1.has_restriction_violation)
        self.assertTrue(self.loc_lvl_1_1_1.restriction_violation_message)

    def test_05(self):
        # Check location creation
        with Form(self.StockLocation) as location_form:
            location_form.name = "Test"

    def test_zero_quant(self):
        """
          Data:
            * Location level_1_1_1 with 2 different products no restriction
        Test Case:
            1. Check restriction message
            2. Change product 1 quant to 0.0
            3. Set restriction 'same' on location level_1_1_1
            4. Check restriction message
        Expected result:
            1. No restriction message
        """
        self.loc_lvl_1_1_1.product_restriction = "any"
        self.assertFalse(self.loc_lvl_1_1_1.has_restriction_violation)
        self.assertFalse(self.loc_lvl_1_1_1.restriction_violation_message)
        self.quant_1_lvl_1_1_1.inventory_quantity = 0.0
        self.quant_1_lvl_1_1_1._apply_inventory()
        self.loc_lvl_1_1_1.product_restriction = "same"
        self.assertFalse(self.loc_lvl_1_1_1.has_restriction_violation)
        self.assertFalse(self.loc_lvl_1_1_1.restriction_violation_message)
