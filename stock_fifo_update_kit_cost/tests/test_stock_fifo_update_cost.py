# Copyright 2017-2020 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class Test_stock_fifo_update_cost(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(Test_stock_fifo_update_cost, self).setUp(*args, **kwargs)

        self.obj_product = self.env["product.product"]
        self.product_ctg_model = self.env["product.category"]
        self.bom_model = self.env["mrp.bom"]
        self.bom_line_model = self.env["mrp.bom.line"]
        self.pick_order = self.env["stock.picking"]
        self.company_partner = self.env.ref("base.main_partner")
        self.customer_location = self.env["ir.model.data"].xmlid_to_object(
            "stock.stock_location_customers"
        )

        self.picking_type_out = self.env["ir.model.data"].xmlid_to_object(
            "stock.picking_type_out"
        )
        self.stock_location = self.env["ir.model.data"].xmlid_to_object(
            "stock.stock_location_stock"
        )

        product_ctg = self.product_ctg_model.create(
            {
                "name": "test_product_ctg",
                "property_valuation": "manual_periodic",
                "property_cost_method": "fifo",
            }
        )

        self.product1 = self.obj_product.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "standard_price": 500.0 ,
                "list_price" : 600.0,
                "categ_id": product_ctg.id,
            }
        )
        self.product2 = self.obj_product.create(
            {
                "name": "Test Product 2",
                "type": "product",
                "standard_price": 1000.0,
                "list_price": 1300.0,
                "categ_id": product_ctg.id,
            }
        )

        self.kitproduct = self.obj_product.create(
            {
                "name": "Test kit",
                "type": "product",
                "standard_price": 0.0,
                "list_price": 2000.0,
                "categ_id": product_ctg.id,
            }
        )

        self.manufacturedProduct = self.obj_product.create(
            {
                "name": "Test mtp",
                "type": "product",
                "standard_price": 0.0,
                "list_price": 2000.0,
                "categ_id": product_ctg.id,
            }
        )
        self.bom_manufacturedProduct_1 = self.bom_model.create(
            {
                "product_tmpl_id": self.manufacturedProduct.product_tmpl_id.id,
                "type": "normal",
                "product_qty": 1,
            }
        )
        self.bom_line_model.create(
            {
                "bom_id": self.bom_manufacturedProduct_1.id,
                "product_id": self.product1.id,
                "product_qty": 1,
            }
        )
        self.bom_line_model.create(
            {
                "bom_id": self.bom_manufacturedProduct_1.id,
                "product_id": self.product2.id,
                "product_qty": 1,
            }
        )

        self.bom_kitproduct_1 = self.bom_model.create(
            {
                "product_tmpl_id": self.kitproduct.product_tmpl_id.id,
                "type": "phantom",
                "product_qty": 1,
            }
        )
        self.bom_line_model.create(
            {
                "bom_id": self.bom_kitproduct_1.id,
                "product_id": self.product1.id,
                "product_qty": 1,
            }
        )

        self.bom_line_model.create(
            {
                "bom_id": self.bom_kitproduct_1.id,
                "product_id": self.product2.id,
                "product_qty": 1,
            }
        )
        self.env["stock.quant"].create(
            {
                "product_id": self.product1.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "quantity": 6.0,
            }
        )
        self.env["stock.quant"].create(
            {
                "product_id": self.product2.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "quantity": 6.0,
            }
        )


    def test_calculate_standard_price_phbom(self):

        self.delivery = self.pick_order.create(
            {
                "picking_type_id": self.picking_type_out.id,
                "partner_id": self.company_partner.id,
                "location_dest_id": self.customer_location.id,
                "location_id": self.stock_location.id,

                "move_lines": [

                    (
                        0,
                        0,
                        {
                            "name": 'move',
                            "company_id": 1,
                            "product_uom_qty": 1.0,
                            "product_uom": self.kitproduct.uom_id.id,
                            "product_id": self.kitproduct.id,
                            "location_dest_id": self.customer_location.id,
                            "location_id": self.stock_location.id,
                        }
                    )
                ],
            }

        )

        self.delivery.action_confirm()
        self.delivery.action_assign()
        self.delivery.move_line_ids.write({'qty_done': 1})
        self.delivery.button_validate()
        self.assertEqual(self.delivery.state, "done")
        self.assertEqual(self.kitproduct.standard_price, self.product1.standard_price +
                         self.product2.standard_price)

    def test_calculate_standard_price_manufacturedbom(self):
        self.delivery = self.pick_order.create(
            {
                "picking_type_id": self.picking_type_out.id,
                "partner_id": self.company_partner.id,
                "location_dest_id": self.customer_location.id,
                "location_id": self.stock_location.id,

                "move_lines": [

                    (
                        0,
                        0,
                        {
                            "name": 'move',
                            "company_id": 1,
                            "product_uom_qty": 1.0,
                            "product_uom": self.manufacturedProduct.uom_id.id,
                            "product_id": self.manufacturedProduct.id,
                            "location_dest_id": self.customer_location.id,
                            "location_id": self.stock_location.id,
                        }
                    )
                ],
            }

        )

        self.delivery.action_confirm()
        self.delivery.action_assign()
        self.delivery.move_lines.quantity_done = 1.0
        self.delivery.button_validate()
        self.assertEqual(self.delivery.state, "done")
        self.assertEqual(self.manufacturedProduct.standard_price, 0)
