from odoo.tests import Form

from .common import StockPickingProductInterchangeableCommon


class TestProduct(StockPickingProductInterchangeableCommon):
    def test_invisible_interchangeable_products(self):
        """
        Test flow to hiding interchangeable table
        for product templates with 2 and more product variants
        """
        self.assertEqual(
            len(self.product_tmpl_napkin.product_variant_ids),
            2,
            msg="Product variants count must be equal to 2",
        )
        with self.assertRaises(AssertionError):
            with Form(
                self.product_tmpl_napkin,
                view="stock_picking_product_interchangeable.product_template_interchangeable_form_view",  # noqa
            ) as form:
                form.product_tmpl_interchangeable_ids.add(self.product_tmpl_plate)

    def test_visible_interchangeable_products(self):
        """
        Test flow to visible interchangeable table
        for product templates with 1 product variant
        """
        self.assertEqual(len(self.product_tmpl_plate.product_variant_ids), 1)
        with Form(
            self.product_tmpl_plate,
            view="stock_picking_product_interchangeable.product_template_interchangeable_form_view",  # noqa
        ) as form:
            form.product_tmpl_interchangeable_ids.add(self.product_chopsticks)
        self.assertEqual(
            len(self.product_tmpl_plate.product_tmpl_interchangeable_ids),
            1,
            msg="Interchangeable products count must be equal to 1",
        )
        self.assertEqual(
            self.product_tmpl_plate.product_tmpl_interchangeable_ids,
            self.product_chopsticks,
            msg="Products must be the same",
        )
