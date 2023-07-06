# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import SUPERUSER_ID
from odoo.tests import common


class TestPurchaseRequestToRfq(common.TransactionCase):
    def setUp(self):
        super(TestPurchaseRequestToRfq, self).setUp()
        self.purchase_request = self.env["purchase.request"]
        self.purchase_request_line = self.env["purchase.request.line"]
        self.wiz = self.env["purchase.request.line.make.purchase.order"]
        self.purchase_order = self.env["purchase.order"]
        vendor = self.env["res.partner"].create({"name": "Partner #2"})
        self.service_product = self.env["product.product"].create(
            {"name": "Product Service Test", "type": "service"}
        )
        self.product_product = self.env["product.product"].create(
            {
                "name": "Product Product Test",
                "type": "product",
                "description_purchase": "Test Description",
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "partner_id": vendor.id,
                "product_tmpl_id": self.service_product.product_tmpl_id.id,
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "partner_id": vendor.id,
                "product_tmpl_id": self.product_product.product_tmpl_id.id,
            }
        )

    def test_purchase_request_allocation(self):
        vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
        }
        purchase_request1 = self.purchase_request.create(vals)
        vals = {
            "request_id": purchase_request1.id,
            "product_id": self.product_product.id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 2.0,
        }
        purchase_request_line1 = self.purchase_request_line.create(vals)
        vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
        }
        purchase_request2 = self.purchase_request.create(vals)
        vals = {
            "request_id": purchase_request1.id,
            "product_id": self.product_product.id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 2.0,
        }
        purchase_request_line2 = self.purchase_request_line.create(vals)
        purchase_request1.button_approved()
        purchase_request2.button_approved()
        purchase_request1.action_view_purchase_request_line()
        vals = {"supplier_id": self.env.ref("base.res_partner_1").id}
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line1.id, purchase_request_line2.id],
        ).create(vals)
        wiz_id.make_purchase_order()
        purchase_request1.action_view_purchase_order()
        po_line = purchase_request_line1.purchase_lines[0]
        # Add unit price in PO Line
        po_line.write({"price_unit": 10})
        purchase = po_line.order_id
        purchase.order_line.action_open_request_line_tree_view()
        purchase.button_confirm()
        purchase_request1.action_view_stock_picking()
        self.assertEqual(purchase_request_line1.qty_in_progress, 2.0)
        self.assertEqual(purchase_request_line2.qty_in_progress, 2.0)
        picking = purchase.picking_ids[0]

        # Check the move
        move = picking.move_ids
        self.assertEqual(move.purchase_request_ids, purchase_request1)
        # Do a move split/merge roundtrip and check that the allocatable
        # quantity remains the same.
        self.assertEqual(
            sum(move.purchase_request_allocation_ids.mapped("open_product_qty")), 4
        )
        split_move = self.env["stock.move"].create(move._split(1))
        split_move._action_confirm(merge=False)
        self.assertEqual(split_move.purchase_request_ids, purchase_request1)
        # The quantity of 4 is now split between the two moves
        self.assertEqual(
            sum(move.purchase_request_allocation_ids.mapped("open_product_qty")), 3
        )
        self.assertEqual(
            sum(split_move.purchase_request_allocation_ids.mapped("open_product_qty")),
            1,
        )
        split_move._merge_moves(merge_into=move)
        self.assertFalse(split_move.exists())
        self.assertEqual(
            sum(move.purchase_request_allocation_ids.mapped("open_product_qty")), 4
        )
        # Reset reserved quantities messed up by the roundtrip
        move._do_unreserve()
        move._action_assign()

        picking.move_line_ids[0].write({"qty_done": 2.0})
        backorder_wiz_id = picking.button_validate()
        common.Form(
            self.env[backorder_wiz_id["res_model"]].with_context(
                **backorder_wiz_id["context"]
            )
        ).save().process()
        request_lines = purchase_request_line1 + purchase_request_line2
        self.assertEqual(sum(request_lines.mapped("qty_done")), 2.0)

        backorder_picking = purchase.picking_ids.filtered(lambda p: p.id != picking.id)
        backorder_picking.move_line_ids[0].write({"qty_done": 1.0})
        backorder_wiz_id2 = backorder_picking.button_validate()
        common.Form(
            self.env[backorder_wiz_id2["res_model"]].with_context(
                **backorder_wiz_id2["context"]
            )
        ).save().process()

        self.assertEqual(sum(request_lines.mapped("qty_done")), 3.0)
        for pick in purchase.picking_ids:
            if pick.state == "assigned":
                pick.action_cancel()
        self.assertEqual(sum(request_lines.mapped("qty_cancelled")), 1.0)
        self.assertEqual(sum(request_lines.mapped("pending_qty_to_receive")), 1.0)

    def test_purchase_request_allocation_services(self):
        vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
            "assigned_to": SUPERUSER_ID,
        }
        purchase_request1 = self.purchase_request.create(vals)
        vals = {
            "request_id": purchase_request1.id,
            "product_id": self.service_product.id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 2.0,
        }
        purchase_request_line1 = self.purchase_request_line.create(vals)
        vals = {"supplier_id": self.env.ref("base.res_partner_1").id}
        purchase_request1.button_approved()
        purchase_request1.action_view_purchase_request_line()
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line", active_ids=[purchase_request_line1.id]
        ).create(vals)
        wiz_id.make_purchase_order()
        purchase_request1.action_view_purchase_order()
        po_line = purchase_request_line1.purchase_lines[0]
        # Add unit price in PO Line
        po_line.write({"price_unit": 10})
        purchase = po_line.order_id
        purchase.button_confirm()
        self.assertEqual(purchase_request_line1.qty_in_progress, 2.0)
        # manually set in the PO line
        po_line.write({"qty_received": 0.5})
        self.assertEqual(purchase_request_line1.qty_done, 0.5)
        purchase.button_cancel()
        self.assertEqual(purchase_request_line1.qty_cancelled, 1.5)
        self.assertEqual(purchase_request_line1.pending_qty_to_receive, 1.5)
        # Case revieve 2 product
        vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
            "assigned_to": SUPERUSER_ID,
        }
        purchase_request2 = self.purchase_request.create(vals)
        vals = {
            "request_id": purchase_request2.id,
            "product_id": self.service_product.id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 2.0,
        }
        purchase_request_line2 = self.purchase_request_line.create(vals)
        vals = {"supplier_id": self.env.ref("base.res_partner_1").id}
        purchase_request2.button_approved()
        purchase_request2.action_view_purchase_request_line()
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line", active_ids=[purchase_request_line2.id]
        ).create(vals)
        wiz_id.make_purchase_order()
        (purchase_request1 + purchase_request2).action_view_purchase_order()
        po_line = purchase_request_line2.purchase_lines[0]
        purchase2 = po_line.order_id
        purchase2.button_confirm()
        self.assertEqual(purchase_request_line2.qty_in_progress, 2.0)
        purchase_request1.action_view_stock_picking()
        # manually set in the PO line
        po_line.write({"qty_received": 2.0})
        self.assertEqual(purchase_request_line2.qty_done, 2.0)

    def test_purchase_request_allocation_min_qty(self):
        vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
        }
        purchase_request1 = self.purchase_request.create(vals)
        vals = {
            "request_id": purchase_request1.id,
            "product_id": self.product_product.id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 2.0,
        }
        purchase_request_line1 = self.purchase_request_line.create(vals)
        # add a vendor
        vendor1 = self.env.ref("base.res_partner_1")
        self.env["product.supplierinfo"].create(
            {
                "partner_id": vendor1.id,
                "product_tmpl_id": self.product_product.product_tmpl_id.id,
                "min_qty": 8,
            }
        )
        vals = {"supplier_id": self.env.ref("base.res_partner_1").id}
        purchase_request1.button_approved()
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line", active_ids=[purchase_request_line1.id]
        ).create(vals)
        wiz_id.make_purchase_order()
        self.assertEqual(
            purchase_request_line1.purchase_request_allocation_ids[0].open_product_qty,
            2.0,
        )

    def test_purchase_request_stock_allocation(self):
        product = self.env.ref("product.product_product_6")
        product.uom_po_id = self.env.ref("uom.product_uom_dozen")

        vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
        }
        purchase_request = self.purchase_request.create(vals)
        vals = {
            "request_id": purchase_request.id,
            "product_id": product.id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 12.0,
        }
        purchase_request_line1 = self.purchase_request_line.create(vals)
        vals = {
            "request_id": purchase_request.id,
            "product_id": product.id,
            "product_uom_id": self.env.ref("uom.product_uom_dozen").id,
            "product_qty": 1,
        }
        purchase_request_line2 = self.purchase_request_line.create(vals)
        vals = {"supplier_id": self.env.ref("base.res_partner_1").id}
        purchase_request.button_approved()
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line",
            active_ids=[purchase_request_line1.id, purchase_request_line2.id],
        ).create(vals)
        # Create PO
        wiz_id.make_purchase_order()
        po_line = purchase_request_line1.purchase_lines[0]
        self.assertEqual(po_line.product_qty, 2, "Quantity should be 2")
        self.assertEqual(
            po_line.product_uom,
            self.env.ref("uom.product_uom_dozen"),
            "The purchase UoM should be Dozen(s).",
        )
        self.assertEqual(
            purchase_request_line1.purchase_request_allocation_ids[
                0
            ].requested_product_uom_qty,
            12.0,
        )
        self.assertEqual(
            purchase_request_line2.purchase_request_allocation_ids[
                0
            ].requested_product_uom_qty,
            1.0,
        )
        purchase = po_line.order_id
        # Cancel PO allocation requested quantity is set to 0.
        purchase.button_cancel()
        self.assertEqual(
            purchase_request_line1.purchase_request_allocation_ids[0].open_product_qty,
            0,
        )
        self.assertEqual(
            purchase_request_line2.purchase_request_allocation_ids[0].open_product_qty,
            0,
        )
        # Set to draft allocation requested quantity is set
        purchase.button_draft()
        self.assertEqual(
            purchase_request_line1.purchase_request_allocation_ids[0].open_product_qty,
            12.0,
        )
        self.assertEqual(
            purchase_request_line2.purchase_request_allocation_ids[0].open_product_qty,
            1.0,
        )
        purchase.button_confirm()
        picking = purchase.picking_ids[0]
        picking.move_line_ids[0].write({"qty_done": 24.0})
        picking.button_validate()
        self.assertEqual(
            purchase_request_line1.purchase_request_allocation_ids[
                0
            ].allocated_product_qty,
            purchase_request_line1.purchase_request_allocation_ids[
                0
            ].requested_product_uom_qty,
        )
        self.assertEqual(
            purchase_request_line2.purchase_request_allocation_ids[
                0
            ].allocated_product_qty,
            purchase_request_line2.purchase_request_allocation_ids[
                0
            ].requested_product_uom_qty,
        )

    def test_purchase_request_stock_allocation_unlink(self):
        product = self.env.ref("product.product_product_6")
        product.uom_po_id = self.env.ref("uom.product_uom_dozen")

        vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
        }
        purchase_request = self.purchase_request.create(vals)
        vals = {
            "request_id": purchase_request.id,
            "product_id": product.id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 12.0,
        }
        purchase_request_line1 = self.purchase_request_line.create(vals)
        vals = {"supplier_id": self.env.ref("base.res_partner_1").id}
        purchase_request.button_approved()
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line", active_ids=[purchase_request_line1.id]
        ).create(vals)
        # Create PO
        wiz_id.make_purchase_order()
        po_line = purchase_request_line1.purchase_lines[0]
        self.assertEqual(
            purchase_request_line1.purchase_request_allocation_ids[
                0
            ].requested_product_uom_qty,
            12.0,
        )
        purchase = po_line.order_id
        purchase.button_cancel()
        # Delete PO: allocation and Purchase Order Lines are unlinked from PRL
        purchase.unlink()
        self.assertEqual(len(purchase_request_line1.purchase_lines), 0)
        self.assertEqual(len(purchase_request_line1.purchase_request_allocation_ids), 0)

    def test_onchange_product_id(self):
        vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
        }
        purchase_request1 = self.purchase_request.create(vals)
        vals = {
            "request_id": purchase_request1.id,
            "product_id": self.product_product.id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 2.0,
        }
        purchase_request_line1 = self.purchase_request_line.create(vals)
        purchase_request_line1.onchange_product_id()

    def test_empty_records_for_company_constraint(self):
        self.assertFalse(self.env["stock.move"]._check_company_purchase_request())

    def test_supplier_assignment(self):
        """Suppliers are not assigned across the company boundary"""
        product = self.env.ref("product.product_product_6")
        product.seller_ids.unlink()
        purchase_request = self.purchase_request.create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "requested_by": SUPERUSER_ID,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        purchase_request_line = self.purchase_request_line.create(
            {
                "request_id": purchase_request.id,
                "product_id": product.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "product_qty": 12.0,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        # A supplier from another company is not assigned
        vendor3 = self.env["res.partner"].create({"name": "Partner #3"})
        supinfo = self.env["product.supplierinfo"].create(
            {
                "partner_id": vendor3.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "company_id": self.env.ref("stock.res_company_1").id,
            }
        )
        self.assertFalse(purchase_request_line.supplier_id)
        # A supplierinfo of a matching company leads to supplier assignment
        vendor4 = self.env["res.partner"].create({"name": "Partner #4"})
        supinfo = self.env["product.supplierinfo"].create(
            {
                "partner_id": vendor4.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        self.assertEqual(purchase_request_line.supplier_id, vendor4)
        supinfo.unlink()
        self.assertFalse(purchase_request_line.supplier_id)
        # A supplierinfo without company leads to supplier assignment as well
        self.env["product.supplierinfo"].create(
            {
                "partner_id": vendor4.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "company_id": False,
            }
        )
        self.assertEqual(purchase_request_line.supplier_id, vendor4)
