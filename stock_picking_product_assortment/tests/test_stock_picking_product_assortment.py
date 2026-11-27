# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests import Form
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockPickingProductAssortment(TransactionCase):
    def setUp(self):
        super().setUp()
        self.filter_obj = self.env["ir.filters"]
        self.product_obj = self.env["product.template"]
        self.stock_picking_obj = self.env["stock.picking"]
        self.pick_type_out = self.env.ref("stock.picking_type_out")
        self.product_category = self.env["product.category"].create(
            {"name": "Test Product category"}
        )
        self.partner_1 = self.env["res.partner"].create({"name": "Test partner 1"})
        self.partner_2 = self.env["res.partner"].create({"name": "Test partner 2"})
        self.product_1 = self.product_obj.create(
            {
                "name": "Test product 1",
                "sale_ok": True,
                "type": "consu",
                "categ_id": self.product_category.id,
                "description_sale": "Test Description Sale",
            }
        )
        self.product_2 = self.product_obj.create(
            {
                "name": "Test product 2",
                "sale_ok": True,
                "type": "consu",
                "categ_id": self.product_category.id,
                "description_sale": "Test Description Sale",
            }
        )

    def test_stock_picking_product_assortment(self):
        assortment_with_whitelist = self.filter_obj.create(
            {
                "name": "Test Assortment 1",
                "model_id": "product.product",
                "domain": [("id", "=", 0)],
                "is_assortment": True,
                "partner_ids": [(4, self.partner_1.id)],
                "whitelist_product_ids": [(4, self.product_1.product_variant_id.id)],
            }
        )
        stock_picking_form = Form(self.stock_picking_obj)
        stock_picking_form.partner_id = self.partner_1
        stock_picking_form.picking_type_id = self.pick_type_out

        stock_picking_1 = stock_picking_form.save()
        self.assertEqual(
            stock_picking_1.assortment_product_ids,
            assortment_with_whitelist.whitelist_product_ids,
        )
        self.assertTrue(stock_picking_1.has_assortment)
        assortment_with_blacklist = self.filter_obj.create(
            {
                "name": "Test Assortment 2",
                "model_id": "product.product",
                "domain": [],
                "is_assortment": True,
                "partner_ids": [(4, self.partner_1.id), (4, self.partner_2.id)],
                "blacklist_product_ids": [(4, self.product_2.product_variant_id.id)],
            }
        )
        stock_picking_form = Form(self.stock_picking_obj)
        stock_picking_form.partner_id = self.partner_1
        stock_picking_form.picking_type_id = self.pick_type_out

        stock_picking_2 = stock_picking_form.save()
        self.assertEqual(
            stock_picking_2.assortment_product_ids,
            assortment_with_whitelist.whitelist_product_ids
            - assortment_with_blacklist.blacklist_product_ids,
        )
        self.assertTrue(stock_picking_2.has_assortment)
        stock_picking_form = Form(self.stock_picking_obj)
        stock_picking_form.partner_id = self.partner_2
        stock_picking_form.picking_type_id = self.pick_type_out

        stock_picking_3 = stock_picking_form.save()
        self.assertFalse(
            stock_picking_3.assortment_product_ids
            & assortment_with_blacklist.blacklist_product_ids
        )
        self.assertTrue(stock_picking_3.has_assortment)

    def test_detailed_operations_product_domain(self):
        self.filter_obj.create(
            {
                "name": "Test Assortment 1",
                "model_id": "product.product",
                "domain": [("id", "=", 0)],
                "is_assortment": True,
                "partner_ids": [(4, self.partner_1.id)],
                "whitelist_product_ids": [(4, self.product_1.product_variant_id.id)],
            }
        )
        stock_picking_form = Form(self.stock_picking_obj)
        stock_picking_form.partner_id = self.partner_1
        stock_picking_form.picking_type_id = self.pick_type_out
        with stock_picking_form.move_ids_without_package.new() as move_form:
            move_form.product_id = self.product_1.product_variant_id
            move_form.product_uom_qty = 1
        picking = stock_picking_form.save()
        picking.action_confirm()
        action = picking.action_detailed_operations()
        # The detailed operations list has no parent record in the web client,
        # so its product domain must only use the move line's own fields.
        arch = (
            self.env["stock.move.line"]
            .with_context(**action["context"])
            .get_view(action["views"][0][0], "list")["arch"]
        )
        product_node = etree.fromstring(arch).xpath("//field[@name='product_id']")[0]
        self.assertNotIn("parent.", product_node.get("domain"))
        self.assertIn("picking_assortment_product_ids", product_node.get("domain"))
        move_line = (
            self.env["stock.move.line"]
            .with_context(**action["context"])
            .create(
                {
                    "product_id": self.product_1.product_variant_id.id,
                    "quantity": 1,
                }
            )
        )
        self.assertTrue(move_line.picking_has_assortment)
        self.assertEqual(
            move_line.picking_assortment_product_ids,
            self.product_1.product_variant_id,
        )
