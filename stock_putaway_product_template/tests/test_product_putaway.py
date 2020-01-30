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
        self.category_services = ref("product.product_category_3")
        self.putaway_line_1 = ref(
            "stock_putaway_product_form.putaway_strat_1_line_1"
        )
        self.putaway_line_2 = ref(
            "stock_putaway_product_form.putaway_strat_1_line_2"
        )
        self.putaway_line_3 = ref(
            "stock_putaway_product_form.putaway_strat_2_line_1"
        )
        self.putaway_line_4 = ref(
            "stock_putaway_product_form.putaway_strat_2_line_2"
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

    def test_tmpl_has_putaways_from_category_simple(self):
        self.assertIn(
            self.putaway_line_2,
            self.product_tmpl_chair.product_putaway_categ_ids,
        )
        self.product_tmpl_chair.categ_id = self.category_services
        self.assertNotIn(
            self.putaway_line_2,
            self.product_tmpl_chair.product_putaway_categ_ids,
        )

    def test_tmpl_has_putaways_from_category_parent(self):
        # chair is under category: all/saleable/office
        self.assertIn(
            self.putaway_line_3,
            self.product_tmpl_chair.product_putaway_categ_ids,
        )
        self.assertNotIn(
            self.putaway_line_4,
            self.product_tmpl_chair.product_putaway_categ_ids,
        )
