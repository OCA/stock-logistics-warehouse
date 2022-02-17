# Copyright 2018-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common


class TestOrderpointPurchaseLink(common.TransactionCase):
    def setUp(self):
        super(TestOrderpointPurchaseLink, self).setUp()

        self.product_obj = self.env["product.product"]
        self.partner_obj = self.env["res.partner"]
        self.pol_obj = self.env["purchase.order.line"]
        self.location_obj = self.env["stock.location"]
        self.orderpoint_obj = self.env["stock.warehouse.orderpoint"]
        self.route_obj = self.env["stock.location.route"]
        self.rule_obj = self.env["stock.rule"]
        self.group_obj = self.env["procurement.group"]

        # WH and routes:
        self.warehouse = self.env.ref("stock.warehouse0")
        self.stock_location = self.warehouse.lot_stock_id
        self.test_location = self.location_obj.create(
            {"name": "Test", "location_id": self.warehouse.view_location_id.id}
        )
        route_buy = self.env.ref("purchase_stock.route_warehouse0_buy").id
        route_test = self.route_obj.create({"name": "Stock to Test"}).id
        self.rule_obj.create(
            {
                "name": "Stock to Test",
                "action": "pull",
                "procure_method": "make_to_order",
                "location_id": self.test_location.id,
                "location_src_id": self.stock_location.id,
                "route_id": route_test,
                "picking_type_id": self.warehouse.int_type_id.id,
                "warehouse_id": self.warehouse.id,
                "group_propagation_option": "none",
            }
        )
        # Partners:
        vendor1 = self.partner_obj.create({"name": "Vendor 1"})

        # Create products:
        self.tp1 = self.product_obj.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "list_price": 150.0,
                "route_ids": [(6, 0, [route_buy, route_test])],
                "seller_ids": [(0, 0, {"name": vendor1.id, "price": 20.0})],
            }
        )

        # Create Orderpoints:
        self.op1 = self.orderpoint_obj.create(
            {
                "product_id": self.tp1.id,
                "location_id": self.stock_location.id,
                "product_min_qty": 5.0,
                "product_max_qty": 20.0,
            }
        )
        self.op2 = self.orderpoint_obj.create(
            {
                "product_id": self.tp1.id,
                "location_id": self.test_location.id,
                "product_min_qty": 5.0,
                "product_max_qty": 20.0,
            }
        )

    def test_01_po_line_from_orderpoints(self):
        """Test that a PO line created/updated by two orderpoints keeps
        the link with both of them."""
        self.group_obj.run_scheduler()
        po_line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.tp1.id)]
        )
        self.assertTrue(po_line)
        # Each orderpoint must have required 20.0 units:
        self.assertEqual(po_line.product_qty, 40.0)
        self.assertEqual(len(po_line.orderpoint_ids), 2)
