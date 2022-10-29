from odoo.tests import TransactionCase


class TestProductProducts(TransactionCase):
    def setUp(self):
        super(TestProductProducts, self).setUp()
        ProductProduct = self.env["product.product"]
        ResPartner = self.env["res.partner"]
        ResUser = self.env["res.users"]
        self.portal_group_id = self.ref("base.group_portal")
        self._icp_sudo = self.env["ir.config_parameter"].sudo()
        self.visible_product_key = (
            "stock_available_portal.portal_visible_products_domain"
        )
        self.visible_user_key = "stock_available_portal.portal_visible_users"
        self.test_user = ResUser.create(
            {
                "login": "test@odoo.com",
                "partner_id": ResPartner.create({"name": "test partner"}).id,
            }
        )
        self.product_test = ProductProduct.create(
            {
                "name": "Test Product",
            }
        )
        self.Product = ProductProduct.with_user(self.test_user)

    def test_computing_access_url(self):
        Product = self.env["product.product"]
        product_test_1 = Product.create({"name": "Test Product #1"})
        format_text = "/my/products/{}"
        self.assertEqual(
            product_test_1.access_url,
            format_text.format(product_test_1.id),
            msg="Product access url must be equal to '/my/products/{}'".format(
                product_test_1.id
            ),
        )
        product_test_2 = Product.create({"name": "Test Product #2"})
        self.assertEqual(
            product_test_2.access_url,
            format_text.format(product_test_2.id),
            msg="Product access url must be equal to '/my/products/{}'".format(
                product_test_2.id
            ),
        )

    def test_get_config_domain(self):
        self._icp_sudo.set_param(self.visible_user_key, "")
        value = self.Product.get_config_domain(self.visible_user_key)
        self.assertEqual(value, [], msg="Value must be equal to empty list")
        self.assertIsInstance(value, list, msg="Value type must be 'list' type")

        self._icp_sudo.set_param(self.visible_user_key, "[]")
        value = self.Product.get_config_domain(self.visible_user_key)
        self.assertEqual(value, [], msg="Value must be equal to []")
        self.assertIsInstance(value, list, msg="Value type must be 'list' type")

        self._icp_sudo.set_param(self.visible_user_key, '[("id", "=", 1)]')
        value = self.Product.get_config_domain(self.visible_user_key)
        self.assertTrue(value, msg="Value must be True")
        self.assertIsInstance(value, list, msg="Value type must be 'list' type")

    def test_access_user_to_portal_products(self):
        self._icp_sudo.set_param(self.visible_user_key, "")
        access = self.Product.check_product_portal_access()
        self.assertFalse(access, msg="Access must be False")
        self._icp_sudo.set_param(self.visible_user_key, "[]")
        access = self.Product.check_product_portal_access()
        self.assertFalse(access, msg="Access must be False")

        self.test_user.write({"groups_id": [(6, 0, [self.portal_group_id])]})

        access = self.Product.check_product_portal_access()
        self.assertTrue(access, msg="Access must be True")

        self._icp_sudo.set_param(
            self.visible_user_key, "[('id', '=', {})]".format(self.test_user.id)
        )
        access = self.Product.check_product_portal_access()
        self.assertTrue(access, msg="Access must be True")

        self._icp_sudo.set_param(self.visible_user_key, "[('id', '=', 1)]")
        access = self.Product.check_product_portal_access()
        self.assertFalse(access, msg="Access must be False")

    def test_get_portal_products(self):
        self.test_user.write({"groups_id": [(6, 0, [self.portal_group_id])]})
        self._icp_sudo.set_param(self.visible_user_key, "[]")
        self._icp_sudo.set_param(self.visible_product_key, "")
        expected_products = self.Product.sudo().search([])
        products = self.Product.get_portal_products([])
        self.assertItemsEqual(expected_products, products, msg="Items must be Equal")
        self._icp_sudo.set_param(self.visible_product_key, "[]")
        products = self.Product.get_portal_products([])
        self.assertItemsEqual(expected_products, products, msg="Items must be Equal")
        self._icp_sudo.set_param(
            self.visible_product_key, "[('id', '=', {})]".format(self.product_test.id)
        )
        products = self.Product.get_portal_products([])
        self.assertEqual(
            products,
            self.product_test,
            msg="Recordset must be equal to 'Test Product' record",
        )
        self._icp_sudo.set_param(self.visible_product_key, "[('id', '=', -1)]")
        products = self.Product.get_portal_products([])
        self.assertFalse(products, msg="Recordset must be empty")
        self._icp_sudo.set_param(self.visible_user_key, "[('id', '=', 1)]")
        products = self.Product.get_portal_products([])
        self.assertFalse(products, msg="Recordset must be empty")
