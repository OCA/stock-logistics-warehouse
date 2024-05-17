# Copyright 2014 Numérigraphe SARL
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.osv.expression import TRUE_LEAF
from odoo.tests.common import TransactionCase


class TestPotentialQty(TransactionCase):
    """Test the potential quantity on a product with a multi-line BoM"""

    @classmethod
    def setUpClass(cls):
        super(TestPotentialQty, cls).setUpClass()

        cls.product_model = cls.env["product.product"]
        cls.bom_model = cls.env["mrp.bom"]
        cls.bom_line_model = cls.env["mrp.bom.line"]
        cls.stock_quant_model = cls.env["stock.quant"]
        cls.config = cls.env["ir.config_parameter"]
        cls.location = cls.env["stock.location"]
        cls.main_company = cls.env.ref("base.main_company")
        # Get the warehouses
        cls.wh_main = cls.env.ref("stock.warehouse0")
        cls.wh_ch = cls.env.ref("stock.stock_warehouse_shop0")

        # We need to compute parent_left and parent_right of the locations as
        # they are used to compute qty_available of the product.
        cls.location._parent_store_compute()
        cls.setup_demo_data()

    @classmethod
    def setup_demo_data(cls):
        #  An interesting product (multi-line BoM, variants)
        cls.tmpl = cls.env.ref("mrp.product_product_table_kit_product_template")
        #  First variant
        cls.var1 = cls.env.ref("mrp.product_product_table_kit")
        cls.var1.type = "product"
        #  Second variant
        cls.var2 = cls.env.ref("stock_available_mrp.product_kit_1a")
        cls.var2.type = "product"
        # Make bolt a stockable product to be able to change its stock
        # we need to unreserve the existing move before being able to do it.
        bolt = cls.env.ref("mrp.product_product_computer_desk_bolt")
        bolt.stock_move_ids._do_unreserve()
        bolt.type = "product"
        # Components that can be used to make the product
        components = [
            # Bolt
            bolt,
            # Wood Panel
            cls.env.ref("mrp.product_product_wood_panel"),
        ]
        # Zero-out the inventory of all variants and components
        for component in components + [v for v in cls.tmpl.product_variant_ids]:
            moves = component.stock_move_ids.filtered(
                lambda mo: mo.state not in ("done", "cancel")
            )
            moves._action_cancel()

            component.stock_quant_ids.unlink()

        #  A product without a BoM
        cls.product_wo_bom = cls.env.ref("product.product_product_11")

        #  Record the initial quantity available for sale
        cls.initial_usable_qties = {
            i.id: i.immediately_usable_qty
            for i in [cls.tmpl, cls.var1, cls.var2, cls.product_wo_bom]
        }

    def create_inventory(self, product, qty, location=None, company_id=None):
        if location is None:
            location = self.wh_main.lot_stock_id
        if company_id:
            self.env["stock.quant"].with_company(company_id)._update_available_quantity(
                product, location, qty
            )
        else:
            self.env["stock.quant"]._update_available_quantity(product, location, qty)

    def create_simple_bom(self, product, sub_product, product_qty=1, sub_product_qty=1):
        bom = self.bom_model.create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_id": product.id,
                "product_qty": product_qty,
            }
        )
        self.bom_line_model.create(
            {
                "bom_id": bom.id,
                "product_id": sub_product.id,
                "product_qty": sub_product_qty,
            }
        )

        return bom

    def assertPotentialQty(self, record, qty, msg):
        record.refresh()
        #  Check the potential
        self.assertEqual(record.potential_qty, qty, msg)
        # Check the variation of quantity available for sale
        self.assertEqual(
            (record.immediately_usable_qty - self.initial_usable_qties[record.id]),
            qty,
            msg,
        )

    def test_01_potential_qty_no_bom(self):
        #  Check the potential when there's no BoM
        self.assertPotentialQty(
            self.product_wo_bom, 0.0, "The potential without a BoM should be 0"
        )

    def test_02_potential_qty_no_bom_for_company(self):
        chicago_id = self.ref("stock.res_company_1")
        # Receive 1000x Wood Panel owned by Chicago
        self.create_inventory(
            product=self.env.ref("mrp.product_product_wood_panel"),
            qty=1000.0,
            location=self.wh_ch.lot_stock_id,
            company_id=chicago_id,
        )
        # Put Bolt owned by Chicago for 1000x the 1st variant in main WH
        self.create_inventory(
            product=self.env.ref("mrp.product_product_computer_desk_bolt"),
            qty=1000.0,
            location=self.wh_ch.lot_stock_id,
            company_id=chicago_id,
        )
        self.assertPotentialQty(
            self.tmpl.with_company(chicago_id),
            250.0,
            "Wrong template potential after receiving components",
        )

        test_user = self.env["res.users"].create(
            {
                "name": "test_demo",
                "login": "test_demo",
                "company_id": self.main_company.id,
                "company_ids": [(4, self.main_company.id), (4, chicago_id)],
                "groups_id": [
                    (4, self.ref("stock.group_stock_user")),
                    (4, self.ref("mrp.group_mrp_user")),
                ],
            }
        )

        bom = self.env["mrp.bom"].search([("product_tmpl_id", "=", self.tmpl.id)])

        test_user_tmpl = self.tmpl.with_user(test_user)
        self.assertPotentialQty(
            test_user_tmpl, 250.0, "Simple user can access to the potential_qty"
        )

        # Set the bom on the main company (visible to members of main company)
        # and all products without company (visible to all)
        # and the demo user on Chicago (child of main company)
        self.env["product.product"].search([TRUE_LEAF]).write({"company_id": False})
        test_user.write({"company_ids": [(6, 0, self.main_company.ids)]})
        bom.company_id = self.main_company
        self.assertPotentialQty(
            test_user_tmpl,
            0,
            "The bom should not be visible to non members of the bom's "
            "company or company child of the bom's company",
        )
        bom.company_id = chicago_id
        test_user.write({"company_ids": [(4, chicago_id)]})
        self.assertPotentialQty(test_user_tmpl, 250.0, "")

    def test_03_potential_qty(self):
        for i in [self.tmpl, self.var1, self.var2]:
            self.assertPotentialQty(i, 0.0, "The potential quantity should start at 0")

        # Receive 1000x Wood Panel
        self.create_inventory(
            product=self.env.ref("mrp.product_product_wood_panel"),
            qty=1000.0,
            location=self.wh_main.lot_stock_id,
        )
        for i in [self.tmpl, self.var1, self.var2]:
            self.assertPotentialQty(
                i,
                0.0,
                "Receiving a single component should not change the "
                "potential of %s" % i,
            )

        # Receive enough bolt to make 1000x the 1st variant in main WH
        self.create_inventory(
            product=self.env.ref("mrp.product_product_computer_desk_bolt"),
            qty=1000.0,
            location=self.wh_main.lot_stock_id,
        )
        self.assertPotentialQty(
            self.tmpl, 250.0, "Wrong template potential after receiving components"
        )
        self.assertPotentialQty(
            self.var1, 250.0, "Wrong variant 1 potential after receiving components"
        )
        self.assertPotentialQty(
            self.var2,
            0.0,
            "Receiving variant 1's component should not change "
            "variant 2's potential",
        )

        # Receive enough components to make 213 the 2nd variant at Chicago
        self.create_inventory(
            self.env.ref("mrp.product_product_wood_panel"),
            1000.0,
            self.wh_ch.lot_stock_id,
            self.ref("stock.res_company_1"),
        )
        self.create_inventory(
            self.env.ref("stock_available_mrp.product_computer_desk_bolt_white"),
            852.0,
            self.wh_ch.lot_stock_id,
            self.ref("stock.res_company_1"),
        )
        self.assertPotentialQty(
            self.tmpl.with_context(test=True),
            250.0,
            "Wrong template potential after receiving components",
        )
        self.assertPotentialQty(
            self.var1,
            250.0,
            "Receiving variant 2's component should not change "
            "variant 1's potential",
        )
        self.assertPotentialQty(
            self.var2.with_company(self.ref("stock.res_company_1")),
            213.0,
            "Wrong variant 2 potential after receiving components",
        )
        # Check by warehouse
        self.assertPotentialQty(
            self.tmpl.with_context(warehouse=self.wh_main.id),
            250.0,
            "Wrong potential quantity in main WH",
        )
        self.assertPotentialQty(
            self.tmpl.with_context(warehouse=self.wh_ch.id),
            213.0,
            "Wrong potential quantity in Chicago WH",
        )
        # Check by location
        self.assertPotentialQty(
            self.tmpl.with_context(location=self.wh_main.lot_stock_id.id),
            250.0,
            "Wrong potential quantity in main WH location",
        )
        self.assertPotentialQty(
            self.tmpl.with_context(location=self.wh_ch.lot_stock_id.id),
            213.0,
            "Wrong potential quantity in Chicago WH location",
        )

    def test_04_multi_unit_recursive_bom(self):
        # Test multi-level and multi-units BOM
        uom_unit = self.env.ref("uom.product_uom_unit")
        uom_unit.rounding = 1.0
        p1 = self.product_model.create(
            {
                "name": "Test product with BOM",
                "type": "product",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        p2 = self.product_model.create(
            {
                "name": "Test sub product with BOM",
                "type": "consu",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        p3 = self.product_model.create(
            {
                "name": "Test component",
                "type": "product",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        bom_p1 = self.bom_model.create(
            {"product_tmpl_id": p1.product_tmpl_id.id, "product_id": p1.id}
        )

        self.bom_line_model.create(
            {
                "bom_id": bom_p1.id,
                "product_id": p3.id,
                "product_qty": 1,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        # Two p2 which have a bom
        self.bom_line_model.create(
            {
                "bom_id": bom_p1.id,
                "product_id": p2.id,
                "product_qty": 2,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        bom_p2 = self.bom_model.create(
            {
                "product_tmpl_id": p2.product_tmpl_id.id,
                "product_id": p2.id,
                "type": "phantom",
            }
        )

        # p2 need 2 unit of component
        self.bom_line_model.create(
            {
                "bom_id": bom_p2.id,
                "product_id": p3.id,
                "product_qty": 2,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        p1.refresh()

        # Need a least 5 units for one P1
        self.assertEqual(0, p1.potential_qty)

        self.create_inventory(p3, 1)
        p1.refresh()
        self.assertEqual(0, p1.potential_qty)

        self.create_inventory(p3, 3)
        p1.refresh()
        self.assertEqual(0, p1.potential_qty)

        self.create_inventory(p3, 5)
        p1.refresh()
        self.assertEqual(1.0, p1.potential_qty)

        self.create_inventory(p3, 6)
        p1.refresh()
        self.assertEqual(3.0, p1.potential_qty)

        self.create_inventory(p3, 10)
        p1.refresh()
        self.assertEqual(5.0, p1.potential_qty)

    def test_05_potential_qty_list(self):
        # Try to highlight a bug when _get_potential_qty is called on
        # a recordset with multiple products
        # Recursive compute is not working

        p1 = self.product_model.create({"name": "Test P1"})
        p2 = self.product_model.create({"name": "Test P2"})
        p3 = self.product_model.create({"name": "Test P3", "type": "product"})

        self.config.set_param("stock_available_mrp_based_on", "immediately_usable_qty")

        # P1 need one P2
        self.create_simple_bom(p1, p2)
        # P2 need one P3
        self.create_simple_bom(p2, p3)

        self.create_inventory(p3, 3)

        self.product_model.invalidate_cache()

        products = self.product_model.search([("id", "in", [p1.id, p2.id, p3.id])])

        self.assertEqual(
            {p1.id: 3.0, p2.id: 3.0, p3.id: 0.0},
            {p.id: p.potential_qty for p in products},
        )

    def test_product_phantom(self):
        # Create a BOM product with 2 components
        # Set stock quantity for the first one == 0.0
        # Set stock quantity for the second one == 1.0
        # Create an incoming movement for the first component
        # The immediately available quantity should stay == 0.0
        uom_unit = self.env.ref("uom.product_uom_unit")
        uom_unit.rounding = 1.0
        product = self.product_model.create(
            {
                "name": "Test product with BOM",
                "type": "product",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        bom = self.bom_model.create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_id": product.id,
                "type": "phantom",
            }
        )

        bom_product = self.product_model.create(
            {
                "name": "BOM product",
                "type": "product",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        self.bom_line_model.create(
            {
                "bom_id": bom.id,
                "product_id": bom_product.id,
                "product_qty": 1,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        bom_product_2 = self.product_model.create(
            {
                "name": "BOM product 2",
                "type": "product",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        self.bom_line_model.create(
            {
                "bom_id": bom.id,
                "product_id": bom_product_2.id,
                "product_qty": 1,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.create_inventory(bom_product_2, 1)

        move_in = self.env["stock.move"].create(
            {
                "name": bom_product.name,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
                "product_id": bom_product.id,
                "product_uom_qty": 1.0,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
            }
        )

        move_in._action_confirm()
        product.invalidate_cache()

        self.assertEqual(product.immediately_usable_qty, 0.0)

    def test_product_siblings(self):
        # This test ensures that always the right bom is used
        # also for products with siblings that also have a bom
        attribute = self.env["product.attribute"].create(
            {
                "name": "Attribute",
                "value_ids": [(0, 0, {"name": "Value1"}), (0, 0, {"name": "Value2"})],
            }
        )
        product_tmpl = self.env["product.template"].create(
            {
                "name": "Template",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, attribute.value_ids.ids)],
                        },
                    )
                ],
            }
        )
        product1, product2 = (
            product_tmpl.product_variant_ids[0],
            product_tmpl.product_variant_ids[1],
        )
        child1 = product1.create(
            {
                "name": "Child1",
                "type": "product",
            }
        )
        child2 = product1.create(
            {
                "name": "Child2",
                "type": "product",
            }
        )
        child3 = product1.create(
            {
                "name": "Child3",
                "type": "product",
            }
        )
        self.create_inventory(child2, 1)
        self.create_inventory(child3, 1)
        bom1 = self.bom_model.create(
            {
                "product_tmpl_id": product_tmpl.id,
                "product_id": product1.id,
                "type": "phantom",
            }
        )
        self.bom_line_model.create(
            {
                "bom_id": bom1.id,
                "product_id": child1.id,
                "product_qty": 1,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.bom_line_model.create(
            {
                "bom_id": bom1.id,
                "product_id": child2.id,
                "product_qty": 1,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        bom2 = self.bom_model.create(
            {
                "product_tmpl_id": product_tmpl.id,
                "product_id": product2.id,
                "type": "phantom",
            }
        )
        self.bom_line_model.create(
            {
                "bom_id": bom2.id,
                "product_id": child2.id,
                "product_qty": 1,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.bom_line_model.create(
            {
                "bom_id": bom2.id,
                "product_id": child3.id,
                "product_qty": 1,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        product1.invalidate_cache()
        product2.invalidate_cache()
        self.assertEqual(product1.immediately_usable_qty, 0)
        self.assertEqual(product2.immediately_usable_qty, 1)
