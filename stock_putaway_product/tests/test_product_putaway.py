# Copyright 2018 Camptocamp SA
# Copyright 2016 Jos De Graeve - Apertoso N.V. <Jos.DeGraeve@apertoso.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductPutaway(TransactionCase):
    def setUp(self):
        super().setUp()
        self.putawayObj = self.env["product.putaway"]
        self.putawayLineObj = self.env["stock.fixed.putaway.strat"]
        ref = self.env.ref
        self.product_tmpl_chair = ref(
            "product.product_product_11_product_template"
        )
        self.product_product_chair = ref("product.product_product_11")
        self.location_chicago_stock = ref("stock.stock_location_shop0")
        self.category_furniture = ref("product.product_category_5")
        self.category_services = ref("product.product_category_3")
        self.putaway_strat_1 = self.putawayObj.create(
            {"name": "Putaway Strategy 1"}
        )
        self.putaway_line_1 = self.putawayLineObj.create(
            {
                "product_id": self.product_product_chair.id,
                "putaway_id": self.putaway_strat_1.id,
                "fixed_location_id": self.location_chicago_stock.id,
            }
        )
        self.putaway_line_2 = self.putawayLineObj.create(
            {
                "category_id": self.category_furniture.id,
                "putaway_id": self.putaway_strat_1.id,
                "fixed_location_id": self.location_chicago_stock.id,
            }
        )

    def test_tmpl_has_putaways_from_products(self):
        self.assertIn(
            self.putaway_line_1,
            self.product_tmpl_chair.product_tmpl_putaway_ids,
        )
        self.putaway_line_1.product_id = self.env["product.product"]
        self.assertNotIn(
            self.putaway_line_1,
            self.product_tmpl_chair.product_tmpl_putaway_ids,
        )

    def test_tmpl_has_putaways_from_category(self):
        self.assertIn(
            self.putaway_line_2,
            self.product_tmpl_chair.product_putaway_categ_ids,
        )
        self.product_tmpl_chair.categ_id = self.category_services
        self.assertNotIn(
            self.putaway_line_2,
            self.product_tmpl_chair.product_putaway_categ_ids,
        )
