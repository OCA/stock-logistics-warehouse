# Copyright (C) 2022 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo.tests import common


class TestApartmentTemplate(common.TransactionCase):
    def setUp(self):
        super(TestApartmentTemplate, self).setUp()

        self.template_obj = self.env["stock.location.content.template"]
        self.content_obj = self.env["stock.location.content.check"]
        self.product_obj = self.env["product.product"]
        self.quant_obj = self.env["stock.quant"]
        self.location_obj = self.env["stock.location"]

        self.categ_id = self.env.ref("product.product_category_all")
        self.parent_location_id = self.env.ref("stock.stock_location_stock")
        self.user_id = self.env.ref("base.user_admin")
        self.company_id = self.env.ref("base.main_company")

        self.product_id_1 = self.product_obj.create(
            {"name": "Body Wash", "type": "product", "categ_id": self.categ_id.id}
        )
        self.product_id_2 = self.product_obj.create(
            {
                "name": "Towel",
                "type": "product",
                "categ_id": self.categ_id.id,
            }
        )

        self.location_id = self.location_obj.create(
            {
                "name": "Apartment Location",
                "location_id": self.parent_location_id.id,
                "usage": "internal",
                "company_id": self.company_id.id,
            }
        )

        self.quant_obj.create(
            {
                "location_id": self.location_id.id,
                "inventory_quantity": 100.0,
                "product_uom_id": self.product_id_1.uom_id.id,
                "product_id": self.product_id_1.id,
                "company_id": self.company_id.id,
            }
        )
        self.quant_obj.create(
            {
                "location_id": self.location_id.id,
                "inventory_quantity": 100.0,
                "product_uom_id": self.product_id_2.uom_id.id,
                "product_id": self.product_id_2.id,
                "company_id": self.company_id.id,
            }
        )

        self.quant_obj.create(
            {
                "location_id": self.parent_location_id.id,
                "inventory_quantity": 100.0,
                "product_uom_id": self.product_id_1.uom_id.id,
                "product_id": self.product_id_1.id,
                "company_id": self.company_id.id,
            }
        )
        self.quant_obj.create(
            {
                "location_id": self.parent_location_id.id,
                "inventory_quantity": 100.0,
                "product_uom_id": self.product_id_2.uom_id.id,
                "product_id": self.product_id_2.id,
                "company_id": self.company_id.id,
            }
        )

    def test_create_location_template(self):
        template_id = self.template_obj.create(
            {
                "name": "Standard",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id_1.id,
                            "quantity": 20.0,
                            "in_checkout": True,
                            "uom_id": self.product_id_1.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id_2.id,
                            "quantity": 20.0,
                            "in_checkout": True,
                            "uom_id": self.product_id_2.uom_id.id,
                        },
                    ),
                ],
            }
        )
        self.location_id.write({"template_id": template_id.id})
        self.parent_location_id.write({"template_id": template_id.id})

    def test_create_content_check(self):
        check_id = self.content_obj.create(
            {
                "date": datetime.datetime.today(),
                "user_id": self.user_id.id,
                "company_id": self.company_id.id,
                "location_id": self.location_id.id,
            }
        )
        check_id._onchange_location_id()
        for line in check_id.line_ids:
            line.counted_qty = 80.0

        check_id.action_confirm()
        check_id.action_complete()
        check_id.action_close()

        check_id_two = check_id.copy()
        check_id_two._onchange_location_id()
        for line_check in check_id_two.line_ids:
            line_check.counted_qty = 50.0
        check_id_two.action_confirm()
        check_id_two.action_cancel()
        check_id_two.action_reset()
        check_id_two.action_confirm()
        check_id_two.action_complete()
        check_id_two.action_close()
