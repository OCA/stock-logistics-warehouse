# Copyright 2016 Cyril Gaudin (Camptocamp)
# Copyright 2019 David Vidal - Tecnativa
# Copyright 2020 Víctor Martínez - Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models
from odoo.exceptions import UserError

from .common import TestOrderpointGeneratorCommon


class TestOrderpointGenerator(TestOrderpointGeneratorCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        config = cls.config_obj.create({"use_product_domain": False})
        config.execute()

    def test_use_product_domain(self):
        """Check the state of the use product domain configuration parameter."""
        self.assertFalse(
            self.orderpoint_template_model.get_use_product_domain_state(),
            msg="Must be disabled",
        )

    def check_orderpoint(self, products, template, fields_dict):
        orderpoints = self.orderpoint_model.search(
            [("name", "=", template.name)], order="product_id"
        )
        self.assertEqual(len(products), len(orderpoints))
        for i, product in enumerate(products):
            self.assertEqual(product, orderpoints[i].product_id)
        for orderpoint in orderpoints:
            for field in fields_dict.keys():
                op_field_value = orderpoint[field]
                if isinstance(orderpoint[field], models.Model):
                    op_field_value = orderpoint[field].id
                self.assertEqual(op_field_value, fields_dict[field])
        return orderpoints

    def wizard_over_products(self, product, template):
        return self.wizard_model.with_context(
            active_model=product._name,
            active_ids=product.ids,
        ).create({"orderpoint_template_id": [(6, 0, template.ids)]})

    def test_product_orderpoint(self):
        products = self.p1 + self.p2
        wizard = self.wizard_over_products(products, self.template)
        wizard.action_configure()
        self.check_orderpoint(products, self.template, self.orderpoint_fields_dict)

    def test_template_orderpoint(self):
        prod_tmpl = self.p1.product_tmpl_id + self.p2.product_tmpl_id
        wizard = self.wizard_over_products(prod_tmpl, self.template)
        wizard.action_configure()
        products = self.p1 + self.p2
        self.check_orderpoint(products, self.template, self.orderpoint_fields_dict)

    def test_template_variants_orderpoint(self):
        self.product_model.create(
            {
                "product_tmpl_id": self.p1.product_tmpl_id.id,
                "name": "Unittest P1 variant",
            }
        )
        wizard = self.wizard_over_products(self.p1.product_tmpl_id, self.template)
        with self.assertRaises(UserError):
            wizard.action_configure()

    def test_auto_qty(self):
        """Compute min and max qty  according to criteria"""
        # Max stock for p1: 100
        self.template.write(
            {
                "auto_min_qty": True,
                "auto_min_date_start": "2019-01-01 01:30:00",
                "auto_min_date_end": "2019-02-01 00:00:00",
                "auto_min_qty_criteria": "max",
            }
        )
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict = self.orderpoint_fields_dict.copy()
        orderpoint_auto_dict.update({"product_min_qty": 100.0})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Min stock for p1: 45
        self.template.write({"auto_min_qty_criteria": "min"})
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_min_qty": 45.0})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Median of stock for p1: 52
        self.template.write({"auto_min_qty_criteria": "median"})
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_min_qty": 52.0})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Average of stock for p1: 60.4
        self.template.write({"auto_min_qty_criteria": "avg"})
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_min_qty": 60.4})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Set auto values for min and max: 60.4 (avg) 100 (max)
        self.template.write(
            {
                "auto_max_qty": True,
                "auto_max_date_start": "2019-01-01 00:00:00",
                "auto_max_date_end": "2019-02-01 00:00:00",
                "auto_max_qty_criteria": "max",
            }
        )
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_max_qty": 100})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # If they have the same values, only one is computed:
        self.template.write({"auto_min_qty_criteria": "max"})
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_min_qty": 100})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Auto min max over a shorter period
        self.template.write(
            {
                "auto_max_date_start": "2019-01-01 02:30:00",
                "auto_max_date_end": "2019-01-01 03:00:00",
                "auto_min_date_start": "2019-01-01 04:00:00",
                "auto_min_date_end": "2019-01-01 06:00:00",
            }
        )
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_min_qty": 55, "product_max_qty": 50})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)
        # Check delivered
        self.template.auto_min_qty_criteria = "delivered"
        self.template.auto_max_qty_criteria = "delivered"
        wizard = self.wizard_over_products(self.p1, self.template)
        wizard.action_configure()
        orderpoint_auto_dict.update({"product_min_qty": 3, "product_max_qty": 5})
        self.check_orderpoint(self.p1, self.template, orderpoint_auto_dict)

    def test_auto_qty_multi_products(self):
        """Each product has a different history"""
        products = self.p1 + self.p2
        self.template.write(
            {
                "auto_min_qty": True,
                "auto_min_date_start": "2019-01-01 00:00:00",
                "auto_min_date_end": "2019-02-01 00:00:00",
                "auto_min_qty_criteria": "max",
            }
        )
        wizard = self.wizard_over_products(products, self.template)
        wizard.action_configure()
        orderpoint_auto_dict = self.orderpoint_fields_dict.copy()
        del orderpoint_auto_dict["product_min_qty"]
        orderpoints = self.check_orderpoint(
            products, self.template, orderpoint_auto_dict
        )
        self.assertEqual(orderpoints[0].product_min_qty, 100)
        self.assertEqual(orderpoints[1].product_min_qty, 1043)

    def test_cron_create_auto_orderpoints(self):
        """Create auto orderpoints from cron"""
        self.orderpoint_template_model._cron_create_auto_orderpoints()
        orderpoints = self.orderpoint_model.search(
            [("product_id", "in", [self.p4.id, self.p5.id])]
        )
        self.assertFalse(orderpoints, msg="Must be created orderpoints")
