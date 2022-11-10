from odoo.tests.common import users

from odoo.addons.stock_multi_warehouse_security.tests.common import TestStockCommon


class TestStockWarehouseAccess(TestStockCommon):
    @users("stock_user_c12_wh2", "stock_user_c1_wh12", "stock_user_c12_wh23")
    def test_setting_preferred_default_warehouse_allowed(self):
        """Even user is not allowed to manage all warehouse
        if the user also sales goods (require sales_stock module) he/she
        must be able to set its default warehouse"""
        if (
            self.env["ir.module.module"]
            .sudo()
            .search(
                [("name", "=", "sale_stock"), ("state", "!=", "installed")],
                limit=1,
            )
        ):
            self.skipTest("skipped because sale_stock is not installed.")

        self.env.user.property_warehouse_id = self.warehouse_1

    @users("stock_user_c12_wh2", "stock_user_c12_wh23")
    def test_reading_all_warehouse(self):
        """I must be able to read other warehouse to set my preferred warehouse"""
        warehouses = self.env["stock.warehouse"].search([])
        self.assertTrue(
            all(
                [
                    wh in warehouses
                    for wh in (self.warehouse_1 | self.warehouse_2 | self.warehouse_3)
                ]
            )
        )

    @users("stock_user_c1_wh12")
    def test_reading_all_warehouse_company_restriction(self):
        """I must be able to read other warehouse to set my preferred warehouse"""
        warehouses = self.env["stock.warehouse"].search([])
        self.assertTrue(
            all([wh in warehouses for wh in (self.warehouse_1 | self.warehouse_2)])
        )
