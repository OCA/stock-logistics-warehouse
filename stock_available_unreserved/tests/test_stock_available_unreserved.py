# Copyright 2018 Camptocamp SA
# Copyright 2016-19 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2019 JARSA Sistemas S.A. de C.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import SavepointCase


class TestStockLogisticsWarehouse(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pickingObj = cls.env["stock.picking"]
        cls.productObj = cls.env["product.product"]
        cls.templateObj = cls.env["product.template"]
        cls.attrObj = cls.env["product.attribute"]
        cls.attrvalueObj = cls.env["product.attribute.value"]

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.main_company = cls.env.ref("base.main_company")

        cls.bin_a = cls.env["stock.location"].create(
            {
                "usage": "internal",
                "name": "Bin A",
                "location_id": cls.stock_location.id,
                "company_id": cls.main_company.id,
            }
        )

        cls.bin_b = cls.env["stock.location"].create(
            {
                "usage": "internal",
                "name": "Bin B",
                "location_id": cls.stock_location.id,
                "company_id": cls.main_company.id,
            }
        )

        cls.env["stock.location"]._parent_store_compute()

        # Create product template
        cls.templateAB = cls.templateObj.create(
            {"name": "templAB", "uom_id": cls.uom_unit.id, "type": "product"}
        )

        # Create product A and B
        cls.color_attribute = cls.attrObj.create({"name": "Color", "sequence": 1})
        cls.color_black = cls.attrvalueObj.create(
            {"name": "Black", "attribute_id": cls.color_attribute.id, "sequence": 1}
        )
        cls.color_white = cls.attrvalueObj.create(
            {"name": "White", "attribute_id": cls.color_attribute.id, "sequence": 2}
        )
        cls.color_grey = cls.attrvalueObj.create(
            {"name": "Grey", "attribute_id": cls.color_attribute.id, "sequence": 3}
        )
        cls.product_attribute_line = cls.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": cls.templateAB.id,
                "attribute_id": cls.color_attribute.id,
                "value_ids": [
                    (6, 0, [cls.color_white.id, cls.color_black.id, cls.color_grey.id])
                ],
            }
        )
        cls.productA = cls.templateAB.product_variant_ids[0]
        cls.productB = cls.templateAB.product_variant_ids[1]

        cls.productC = cls.templateAB.product_variant_ids[2]

        # Create a picking move from INCOMING to STOCK
        cls.pickingInA = cls.pickingObj.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.stock_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": cls.productA.id,
                            "product_uom": cls.productA.uom_id.id,
                            "product_uom_qty": 2,
                            "quantity_done": 2,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.stock_location.id,
                        },
                    )
                ],
            }
        )

        cls.pickingInB = cls.pickingObj.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.stock_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": cls.productB.id,
                            "product_uom": cls.productB.uom_id.id,
                            "product_uom_qty": 3,
                            "quantity_done": 3,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.stock_location.id,
                        },
                    )
                ],
            }
        )
        cls.pickingOutA = cls.pickingObj.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": cls.productB.id,
                            "product_uom": cls.productB.uom_id.id,
                            "product_uom_qty": 2,
                            "location_id": cls.stock_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    )
                ],
            }
        )

    def compare_qty_available_not_res(self, product, value):
        product.invalidate_cache()
        self.assertEqual(product.qty_available_not_res, value)

    def test_01_stock_levels(self):
        """checking that qty_available_not_res actually reflects \
        the variations in stock, both on product and template"""

        self.compare_qty_available_not_res(self.productA, 0)
        self.compare_qty_available_not_res(self.templateAB, 0)

        self.pickingInA.action_confirm()
        self.compare_qty_available_not_res(self.productA, 0)
        self.compare_qty_available_not_res(self.templateAB, 0)

        self.pickingInA.action_assign()
        self.compare_qty_available_not_res(self.productA, 0)
        self.compare_qty_available_not_res(self.templateAB, 0)

        self.pickingInA.button_validate()
        self.compare_qty_available_not_res(self.productA, 2)
        self.compare_qty_available_not_res(self.templateAB, 2)

        # will directly trigger action_done on self.productB
        self.pickingInB.action_done()
        self.compare_qty_available_not_res(self.productA, 2)
        self.compare_qty_available_not_res(self.productB, 3)
        self.compare_qty_available_not_res(self.templateAB, 5)

        self.compare_qty_available_not_res(self.productB, 3)
        self.compare_qty_available_not_res(self.templateAB, 5)

        self.pickingOutA.action_confirm()
        self.compare_qty_available_not_res(self.productB, 3)
        self.compare_qty_available_not_res(self.templateAB, 5)

        self.pickingOutA.action_assign()
        self.compare_qty_available_not_res(self.productB, 1)
        self.compare_qty_available_not_res(self.templateAB, 3)

        self.pickingOutA.action_done()
        self.compare_qty_available_not_res(self.productB, 1)
        self.compare_qty_available_not_res(self.templateAB, 3)

        self.templateAB.action_open_quants_unreserved()

    def test_02_more_than_one_quant(self):
        self.env["stock.quant"].create(
            {
                "location_id": self.stock_location.id,
                "company_id": self.main_company.id,
                "product_id": self.productA.id,
                "quantity": 10.0,
            }
        )
        self.env["stock.quant"].create(
            {
                "location_id": self.bin_a.id,
                "company_id": self.main_company.id,
                "product_id": self.productA.id,
                "quantity": 10.0,
            }
        )
        self.env["stock.quant"].create(
            {
                "location_id": self.bin_b.id,
                "company_id": self.main_company.id,
                "product_id": self.productA.id,
                "quantity": 60.0,
            }
        )
        self.compare_qty_available_not_res(self.productA, 80)

    def check_variants_found_correctly(self, operator, value, expected):
        domain = [("id", "in", self.templateAB.product_variant_ids.ids)]
        return self.check_found_correctly(
            self.env["product.product"], domain, operator, value, expected
        )

    def check_template_found_correctly(self, operator, value, expected):
        # There may be other products already in the system: ignore those
        domain = [("id", "in", self.templateAB.ids)]
        return self.check_found_correctly(
            self.env["product.template"], domain, operator, value, expected
        )

    def check_found_correctly(self, model, domain, operator, value, expected):
        found = model.search(domain + [("qty_available_not_res", operator, value)])
        if found != expected:
            self.fail(
                "Searching for products failed: search for unreserved "
                "quantity {operator} {value}; expected to find "
                "{expected}, but found {found}".format(
                    operator=operator,
                    value=value,
                    expected=expected or "no products",
                    found=found,
                )
            )

    def test_03_stock_search(self):
        all_variants = self.templateAB.product_variant_ids
        a_and_b = self.productA + self.productB
        b_and_c = self.productB + self.productC
        a_and_c = self.productA + self.productC
        no_variants = self.env["product.product"]
        no_template = self.env["product.template"]
        # Start: one template with three variants.
        # All variants have zero unreserved stock
        self.check_variants_found_correctly("=", 0, all_variants)
        self.check_variants_found_correctly(">=", 0, all_variants)
        self.check_variants_found_correctly("<=", 0, all_variants)
        self.check_variants_found_correctly(">", 0, no_variants)
        self.check_variants_found_correctly("<", 0, no_variants)
        self.check_variants_found_correctly("!=", 0, no_variants)

        self.check_template_found_correctly("=", 0, self.templateAB)
        self.check_template_found_correctly(">=", 0, self.templateAB)
        self.check_template_found_correctly("<=", 0, self.templateAB)
        self.check_template_found_correctly(">", 0, no_template)
        self.check_template_found_correctly("<", 0, no_template)
        self.check_template_found_correctly("!=", 0, no_template)

        self.pickingInA.action_confirm()
        # All variants still have zero unreserved stock
        self.check_variants_found_correctly("=", 0, all_variants)
        self.check_variants_found_correctly(">=", 0, all_variants)
        self.check_variants_found_correctly("<=", 0, all_variants)
        self.check_variants_found_correctly(">", 0, no_variants)
        self.check_variants_found_correctly("<", 0, no_variants)
        self.check_variants_found_correctly("!=", 0, no_variants)

        self.check_template_found_correctly("=", 0, self.templateAB)
        self.check_template_found_correctly(">=", 0, self.templateAB)
        self.check_template_found_correctly("<=", 0, self.templateAB)
        self.check_template_found_correctly(">", 0, no_template)
        self.check_template_found_correctly("<", 0, no_template)
        self.check_template_found_correctly("!=", 0, no_template)

        self.pickingInA.action_assign()
        # All variants still have zero unreserved stock
        self.check_variants_found_correctly("=", 0, all_variants)
        self.check_variants_found_correctly(">=", 0, all_variants)
        self.check_variants_found_correctly("<=", 0, all_variants)
        self.check_variants_found_correctly(">", 0, no_variants)
        self.check_variants_found_correctly("<", 0, no_variants)
        self.check_variants_found_correctly("!=", 0, no_variants)

        self.check_template_found_correctly("=", 0, self.templateAB)
        self.check_template_found_correctly(">=", 0, self.templateAB)
        self.check_template_found_correctly("<=", 0, self.templateAB)
        self.check_template_found_correctly(">", 0, no_template)
        self.check_template_found_correctly("<", 0, no_template)
        self.check_template_found_correctly("!=", 0, no_template)

        self.pickingInA.button_validate()
        # product A has 2 unreserved stock, other variants have 0

        self.check_variants_found_correctly("=", 2, self.productA)
        self.check_variants_found_correctly("=", 0, b_and_c)
        self.check_variants_found_correctly(">", 0, self.productA)
        self.check_variants_found_correctly("<", 0, no_variants)
        self.check_variants_found_correctly("!=", 0, self.productA)
        self.check_variants_found_correctly("!=", 1, all_variants)
        self.check_variants_found_correctly("!=", 2, b_and_c)
        self.check_variants_found_correctly("<=", 0, b_and_c)
        self.check_variants_found_correctly("<=", 1, b_and_c)
        self.check_variants_found_correctly(">=", 0, all_variants)
        self.check_variants_found_correctly(">=", 1, self.productA)

        self.check_template_found_correctly("=", 0, self.templateAB)
        self.check_template_found_correctly("=", 1, no_template)
        self.check_template_found_correctly("=", 2, self.templateAB)
        self.check_template_found_correctly("!=", 0, self.templateAB)
        self.check_template_found_correctly("!=", 1, self.templateAB)
        self.check_template_found_correctly("!=", 2, self.templateAB)
        self.check_template_found_correctly(">", -1, self.templateAB)
        self.check_template_found_correctly(">", 0, self.templateAB)
        self.check_template_found_correctly(">", 1, self.templateAB)
        self.check_template_found_correctly(">", 2, no_template)
        self.check_template_found_correctly("<", 3, self.templateAB)
        self.check_template_found_correctly("<", 2, self.templateAB)
        self.check_template_found_correctly("<", 1, self.templateAB)
        self.check_template_found_correctly("<", 0, no_template)
        self.check_template_found_correctly(">=", 0, self.templateAB)
        self.check_template_found_correctly(">=", 1, self.templateAB)
        self.check_template_found_correctly(">=", 2, self.templateAB)
        self.check_template_found_correctly(">=", 3, no_template)
        self.check_template_found_correctly("<=", 3, self.templateAB)
        self.check_template_found_correctly("<=", 2, self.templateAB)
        self.check_template_found_correctly("<=", 1, self.templateAB)
        self.check_template_found_correctly("<=", 0, self.templateAB)
        self.check_template_found_correctly("<=", -1, no_template)

        self.pickingInB.action_done()
        # product A has 2 unreserved, product B has 3 unreserved and
        # the remaining variant has 0

        self.check_variants_found_correctly("=", 2, self.productA)
        self.check_variants_found_correctly("=", 3, self.productB)
        self.check_variants_found_correctly("=", 0, self.productC)
        self.check_variants_found_correctly(">", 0, a_and_b)
        self.check_variants_found_correctly("<", 0, no_variants)
        self.check_variants_found_correctly("!=", 0, a_and_b)
        self.check_variants_found_correctly("!=", 1, all_variants)
        self.check_variants_found_correctly("!=", 2, b_and_c)
        self.check_variants_found_correctly("!=", 3, a_and_c)
        self.check_variants_found_correctly("<=", 0, self.productC)
        self.check_variants_found_correctly("<=", 1, self.productC)
        self.check_variants_found_correctly(">=", 0, all_variants)
        self.check_variants_found_correctly(">=", 1, a_and_b)
        self.check_variants_found_correctly(">=", 2, a_and_b)
        self.check_variants_found_correctly(">=", 3, self.productB)
        self.check_variants_found_correctly(">=", 4, no_variants)

        self.check_template_found_correctly("=", 0, self.templateAB)
        self.check_template_found_correctly("=", 1, no_template)
        self.check_template_found_correctly("=", 2, self.templateAB)
        self.check_template_found_correctly("=", 3, self.templateAB)
        self.check_template_found_correctly("!=", 0, self.templateAB)
        self.check_template_found_correctly("!=", 2, self.templateAB)
        self.check_template_found_correctly("!=", 3, self.templateAB)
        self.check_template_found_correctly(">", 1, self.templateAB)
        self.check_template_found_correctly(">", 2, self.templateAB)
        # This part may seem a bit unintuitive, but this is the
        # way it works in the Odoo core
        # Searches are "deferred" to the variants, so while the template says
        # it has a stock of 5, searching for a stock greater than 3 will not
        # find anything because no singular variant has a higher stock
        self.check_template_found_correctly(">", 3, no_template)
        self.check_template_found_correctly("<", 3, self.templateAB)
        self.check_template_found_correctly("<", 2, self.templateAB)
        self.check_template_found_correctly("<", 1, self.templateAB)
        self.check_template_found_correctly("<", 0, no_template)
