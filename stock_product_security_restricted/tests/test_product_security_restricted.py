# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestProductSecurityRestricted(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create security groups with proper implied IDs
        cls.group_product_creation = cls.env.ref(
            "stock_product_security_restricted.group_product_creation"
        )
        cls.group_product_creation_restricted = cls.env.ref(
            "stock_product_security_restricted.group_product_creation_restricted"
        )

        # Create test users
        cls.user_product_creation = cls.env["res.users"].create(
            {
                "name": "Product Creation User",
                "login": "product_creation_user",
                "email": "product_creation@test.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.group_product_creation.id,
                            cls.env.ref("stock.group_stock_user").id,
                        ],
                    )
                ],
            }
        )

        cls.user_product_creation_restricted = cls.env["res.users"].create(
            {
                "name": "Product Creation Restricted User",
                "login": "product_creation_restricted_user",
                "email": "product_restricted@test.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.group_product_creation_restricted.id,
                            cls.group_product_creation.id,
                            cls.env.ref("stock.group_stock_user").id,
                        ],
                    )
                ],
            }
        )

        # Create product categories
        cls.category_not_restricted = cls.env["product.category"].create(
            {
                "name": "Not Restricted Category",
                "restricted_access": False,
            }
        )

        cls.category_restricted = cls.env["product.category"].create(
            {
                "name": "Restricted Category",
                "restricted_access": True,
            }
        )

        # Create warehouses
        cls.warehouse_not_restricted = cls.env["stock.warehouse"].create(
            {
                "name": "Not Restricted Warehouse",
                "code": "NRW",
                "restricted_access": False,
            }
        )

        cls.warehouse_restricted = cls.env["stock.warehouse"].create(
            {
                "name": "Restricted Warehouse",
                "code": "RW",
                "restricted_access": True,
            }
        )

        # Create products
        cls.product_not_restricted = cls.env["product.product"].create(
            {
                "name": "Not Restricted Product",
                "categ_id": cls.category_not_restricted.id,
            }
        )

        cls.product_restricted = cls.env["product.product"].create(
            {
                "name": "Restricted Product",
                "categ_id": cls.category_restricted.id,
            }
        )

        # Create BOMs
        cls.bom_not_restricted = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_not_restricted.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )

        cls.bom_restricted = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_restricted.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )

    def test_product_creation_user_can_edit_non_restricted_products(self):
        """Test that Product Creation user can edit non-restricted products"""
        product = self.product_not_restricted.with_user(self.user_product_creation)
        product.write({"name": "Updated Product Name"})
        self.assertEqual(product.name, "Updated Product Name")

    def test_product_creation_user_cannot_edit_restricted_products(self):
        """Test that Product Creation user cannot edit restricted products"""
        product = self.product_restricted.with_user(self.user_product_creation)
        with self.assertRaises(AccessError):
            product.write({"name": "Should Fail"})

    def test_product_creation_user_can_create_non_restricted_products(self):
        """Test that Product Creation user can create non-restricted products"""
        product = (
            self.env["product.product"]
            .with_user(self.user_product_creation)
            .create(
                {
                    "name": "New Non-Restricted Product",
                    "categ_id": self.category_not_restricted.id,
                }
            )
        )
        self.assertTrue(product.id)

    def test_product_creation_user_cannot_create_restricted_products(self):
        """Test that Product Creation user cannot create restricted products"""
        with self.assertRaises(AccessError):
            self.env["product.product"].with_user(self.user_product_creation).create(
                {
                    "name": "New Restricted Product",
                    "categ_id": self.category_restricted.id,
                }
            )

    def test_product_creation_restricted_user_can_edit_all_products(self):
        """Test that Restricted user can edit all products"""
        # Edit non-restricted product
        product_nr = self.product_not_restricted.with_user(
            self.user_product_creation_restricted
        )
        product_nr.write({"name": "Updated Non-Restricted"})
        self.assertEqual(product_nr.name, "Updated Non-Restricted")

        # Edit restricted product
        product_r = self.product_restricted.with_user(
            self.user_product_creation_restricted
        )
        product_r.write({"name": "Updated Restricted"})
        self.assertEqual(product_r.name, "Updated Restricted")

    def test_product_creation_user_can_edit_non_restricted_boms(self):
        """Test that Product Creation user can edit non-restricted BOMs"""
        bom = self.bom_not_restricted.with_user(self.user_product_creation)
        bom.write({"product_qty": 2.0})
        self.assertEqual(bom.product_qty, 2.0)

    def test_product_creation_user_cannot_edit_restricted_boms(self):
        """Test that Product Creation user cannot edit restricted BOMs"""
        bom = self.bom_restricted.with_user(self.user_product_creation)
        with self.assertRaises(AccessError):
            bom.write({"product_qty": 2.0})

    def test_product_creation_restricted_user_can_edit_all_boms(self):
        """Test that Restricted user can edit all BOMs"""
        # Edit non-restricted BOM
        bom_nr = self.bom_not_restricted.with_user(
            self.user_product_creation_restricted
        )
        bom_nr.write({"product_qty": 3.0})
        self.assertEqual(bom_nr.product_qty, 3.0)

        # Edit restricted BOM
        bom_r = self.bom_restricted.with_user(self.user_product_creation_restricted)
        bom_r.write({"product_qty": 4.0})
        self.assertEqual(bom_r.product_qty, 4.0)

    def test_product_creation_restricted_user_can_edit_categories(self):
        """Test that Restricted user can edit categories"""
        category = self.category_not_restricted.with_user(
            self.user_product_creation_restricted
        )
        category.write({"name": "Updated Category"})
        self.assertEqual(category.name, "Updated Category")

    def test_product_creation_user_can_edit_non_restricted_locations(self):
        """Test that Product Creation user can edit non-restricted locations"""
        location = (
            self.env["stock.location"]
            .with_user(self.user_product_creation)
            .create(
                {
                    "name": "Non-Restricted Location",
                    "warehouse_id": self.warehouse_not_restricted.id,
                    "location_id": self.warehouse_not_restricted.lot_stock_id.id,
                }
            )
        )
        self.assertTrue(location.id)

    def test_product_creation_user_cannot_edit_restricted_locations(self):
        """Test that Product Creation user cannot edit restricted locations"""
        with self.assertRaises(AccessError):
            self.env["stock.location"].with_user(self.user_product_creation).create(
                {
                    "name": "Restricted Location",
                    "warehouse_id": self.warehouse_restricted.id,
                    "location_id": self.warehouse_restricted.lot_stock_id.id,
                }
            )

    def test_product_creation_restricted_user_can_edit_all_locations(self):
        """Test that Restricted user can edit all locations"""
        # Create location in non-restricted warehouse
        location_nr = (
            self.env["stock.location"]
            .with_user(self.user_product_creation_restricted)
            .create(
                {
                    "name": "Non-Restricted Location",
                    "warehouse_id": self.warehouse_not_restricted.id,
                    "location_id": self.warehouse_not_restricted.lot_stock_id.id,
                }
            )
        )
        self.assertTrue(location_nr.id)

        # Create location in restricted warehouse
        location_r = (
            self.env["stock.location"]
            .with_user(self.user_product_creation_restricted)
            .create(
                {
                    "name": "Restricted Location",
                    "warehouse_id": self.warehouse_restricted.id,
                    "location_id": self.warehouse_restricted.lot_stock_id.id,
                }
            )
        )
        self.assertTrue(location_r.id)

    def test_product_template_access_follows_category_restriction(self):
        """Test that product.template follows category restriction rules"""
        template_nr = self.product_not_restricted.product_tmpl_id.with_user(
            self.user_product_creation
        )
        template_nr.write({"name": "Updated Template"})
        self.assertEqual(template_nr.name, "Updated Template")

        template_r = self.product_restricted.product_tmpl_id.with_user(
            self.user_product_creation
        )
        with self.assertRaises(AccessError):
            template_r.write({"name": "Should Fail"})
