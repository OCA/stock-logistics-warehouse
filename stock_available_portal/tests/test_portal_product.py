from odoo.tests import tagged

from odoo.addons.base.tests.common import HttpCaseWithUserPortal
from odoo.addons.stock_available_portal.controllers.portal import PortalProduct


@tagged("post_install", "-at_install")
class TestWebsitePriceListHttp(HttpCaseWithUserPortal):
    def test_access_portal_products(self):
        product = self.env["product.product"].search([], limit=1)
        session = self.authenticate("portal", "portal")
        r = self.url_open("/my/products")
        self.assertEqual(r.status_code, 200, msg="Status code must be equal to 200")
        self.assertEqual(
            r.request.path_url,
            "/my/products",
            msg="Url path must be equal to '/my/products'",
        )
        r = self.url_open("/my/products?search_in=all&search=test")
        self.assertEqual(r.status_code, 200, msg="Status code must be equal to 200")
        self.assertEqual(
            r.request.path_url,
            "/my/products?search_in=all&search=test",
            msg="Url path must be equal to '/my/products?search_in=all&search=test'",
        )
        r = self.url_open("/my/products/{}".format(product.id))
        self.assertEqual(r.status_code, 200, msg="Status code must be equal to 200")
        self.assertEqual(
            r.request.path_url,
            "/my/products/{}".format(product.id),
            msg="Url path must be equal to '/my/products/{}'".format(product.id),
        )
        self.env["ir.config_parameter"].set_param(
            "stock_available_portal.portal_visible_users", "[('id', '=', 1)]"
        )
        r = self.url_open("/my/products")
        self.assertEqual(r.status_code, 200, msg="Status code must be equal to 200")
        self.assertEqual(
            r.request.path_url, "/my/home", msg="Url path must be equal to '/my/home'"
        )
        r = self.url_open("/my/products/{}".format(product.id))
        self.assertEqual(r.status_code, 200, msg="Status code must be equal to 200")
        self.assertEqual(
            r.request.path_url, "/my/home", msg="Url path must be equal to '/my/home'"
        )
        self.env["ir.config_parameter"].set_param(
            "stock_available_portal.portal_visible_users",
            "[('id', '=', {})]".format(session.uid),
        )
        r = self.url_open("/my/products")
        self.assertEqual(r.status_code, 200, msg="Status code must be equal to 200")
        self.assertEqual(
            r.request.path_url,
            "/my/products",
            msg="Url path must be equal to '/my/products'",
        )

    def test_get_product_searchbar_sorting(self):
        obj = PortalProduct()
        searched_bar = obj._get_product_searchbar_sorting()
        keys = list(searched_bar.keys())
        expected_keys = ["date", "name", "default_code"]
        self.assertListEqual(keys, expected_keys, msg="Keys list must be the same")

        date_obj = searched_bar.get("date")
        self.assertEqual(
            date_obj.get("order"),
            "create_date desc",
            msg="Order must be equal to 'create_date desc'",
        )
        name_obj = searched_bar.get("name")
        self.assertEqual(
            name_obj.get("order"), "name", msg="Order must be equal to 'name'"
        )
        default_code_obj = searched_bar.get("default_code")
        self.assertEqual(
            default_code_obj.get("order"),
            "default_code",
            msg="Order must be equal to 'default_code'",
        )

    def test_get_product_searchbar_filters(self):
        obj = PortalProduct()
        searchbar_filter = obj._get_product_searchbar_filters()
        keys = list(searchbar_filter.keys())
        expected_keys = ["all"]
        self.assertListEqual(keys, expected_keys, msg="Keys list must be the same")
        all_obj = searchbar_filter.get("all")
        self.assertEqual(all_obj.get("domain"), [], msg="Domain must be empty")

    def test_get_searchbar_inputs(self):
        obj = PortalProduct()
        searchbar_input = obj._get_searchbar_inputs()
        keys = list(searchbar_input.keys())
        expected_keys = ["all", "default_code", "name"]
        self.assertListEqual(keys, expected_keys, msg="Keys list must be the same")
        all_obj = searchbar_input.get("all")
        self.assertEqual(
            all_obj.get("input"), "all", msg="Input value must be equal to 'all'"
        )
        default_code_obj = searchbar_input.get("default_code")
        self.assertEqual(
            default_code_obj.get("input"),
            "default_code",
            msg="Input value must be equal to 'default_code'",
        )
        name_obj = searchbar_input.get("name")
        self.assertEqual(
            name_obj.get("input"),
            "display_name",
            msg="Input value must be equal to 'display_name'",
        )

    def test_get_search_domain(self):
        obj = PortalProduct()
        self.assertEqual(
            obj._get_search_domain(None, None),
            [],
            msg="Function must be return empty list",
        )
        self.assertEqual(
            obj._get_search_domain("other", "other"),
            [],
            msg="Function must br return empty list",
        )
        expected_domain = [("name", "ilike", "test")]
        self.assertEqual(
            obj._get_search_domain("name", "test"),
            expected_domain,
            msg="Domains must be the same",
        )
        expected_domain = [("default_code", "ilike", "test")]
        self.assertEqual(
            obj._get_search_domain("default_code", "test"),
            expected_domain,
            msg="Domains must be the same",
        )
        expected_domain = [
            "|",
            ("name", "ilike", "test"),
            ("default_code", "ilike", "test"),
        ]
        self.assertEqual(
            obj._get_search_domain("all", "test"),
            expected_domain,
            msg="Domains must be the same",
        )

    def test_prepare_home_portal_values(self):
        obj = PortalProduct()
        result = obj._prepare_home_portal_values([])
        self.assertEqual(result, {}, msg="Function must be return empty dict")
