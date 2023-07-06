# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import SUPERUSER_ID, exceptions
from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestPurchaseRequest(TransactionCase):
    def setUp(self):
        super(TestPurchaseRequest, self).setUp()
        self.purchase_request_obj = self.env["purchase.request"]
        self.purchase_request_line_obj = self.env["purchase.request.line"]
        self.purchase_order = self.env["purchase.order"]
        self.wiz = self.env["purchase.request.line.make.purchase.order"]
        self.picking_type_id = self.env.ref("stock.picking_type_in")
        vals = {
            "group_id": self.env["procurement.group"].create({}).id,
            "picking_type_id": self.picking_type_id.id,
            "requested_by": SUPERUSER_ID,
        }
        self.purchase_request = self.purchase_request_obj.create(vals)
        vals = {
            "request_id": self.purchase_request.id,
            "product_id": self.env.ref("product.product_product_13").id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 5.0,
        }
        self.purchase_request_line_obj.create(vals)

    def test_purchase_request_line_action(self):
        action = self.purchase_request.line_ids.action_show_details()
        self.assertEqual(action["res_id"], self.purchase_request.line_ids.id)

    def test_purchase_request_status(self):
        """Tests Purchase Request status workflow."""
        purchase_request = self.purchase_request
        purchase_request.write({"assigned_to": SUPERUSER_ID})
        self.assertEqual(purchase_request.is_editable, True, "Should be editable")
        self.assertEqual(purchase_request.state, "draft", "Should be in state draft")
        purchase_request.button_to_approve()
        self.assertEqual(
            purchase_request.state, "to_approve", "Should be in state to_approve"
        )
        with self.assertRaises(exceptions.UserError) as e:
            purchase_request.unlink()
        msg = "You cannot delete a purchase request which is not draft."
        self.assertIn(msg, e.exception.args[0])
        self.assertEqual(purchase_request.is_editable, False, "Should not be editable")
        purchase_request.button_draft()
        self.assertEqual(purchase_request.is_editable, True, "Should be editable")
        self.assertEqual(purchase_request.state, "draft", "Should be in state draft")
        purchase_request.button_to_approve()
        purchase_request.button_done()
        self.assertEqual(purchase_request.is_editable, False, "Should not be editable")
        with self.assertRaises(exceptions.UserError) as e:
            purchase_request.unlink()
        msg = "You cannot delete a purchase request which is not draft."
        self.assertIn(msg, e.exception.args[0])
        purchase_request.button_rejected()
        self.assertEqual(purchase_request.is_editable, False, "Should not be editable")
        vals = {
            "request_id": purchase_request.id,
            "product_id": self.env.ref("product.product_product_6").id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 2.0,
        }
        purchase_request_line = self.purchase_request_line_obj.create(vals)
        purchase_request.button_approved()
        vals = {"supplier_id": self.env.ref("base.res_partner_1").id}

        # It is required to have a picking type
        purchase_request.picking_type_id = False
        with self.assertRaisesRegex(UserError, "a Picking Type"):
            self.wiz.with_context(
                active_model="purchase.request",
                active_ids=[purchase_request.id],
            ).create(vals)
        purchase_request.picking_type_id = self.picking_type_id

        # Picking type across all lines have to be the same
        purchase_request2 = purchase_request.copy(
            {"picking_type_id": self.picking_type_id.copy().id}
        )
        purchase_request2.button_approved()
        with self.assertRaisesRegex(UserError, "same Picking Type"):
            self.wiz.with_context(
                active_model="purchase.request.line",
                active_ids=(purchase_request_line + purchase_request2.line_ids).ids,
            ).create(vals)

        purchase_request2.picking_type_id = purchase_request.picking_type_id
        purchase_request2.group_id = self.env["procurement.group"].create({})
        with self.assertRaisesRegex(UserError, "different procurement group"):
            self.wiz.with_context(
                active_model="purchase.request.line",
                active_ids=(purchase_request_line + purchase_request2.line_ids).ids,
            ).create(vals)

        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line", active_ids=[purchase_request_line.id]
        ).create(vals)
        wiz_id.make_purchase_order()
        # Unlink purchase_lines from state approved
        with self.assertRaises(UserError):
            purchase_request_line.unlink()
        purchase = purchase_request_line.purchase_lines.order_id
        purchase.button_done()
        self.assertEqual(purchase.state, "done")

        with self.assertRaisesRegex(
            UserError, "The purchase has already been completed"
        ):
            self.wiz.with_context(
                active_model="purchase.request.line",
                active_ids=[purchase_request_line.id],
            ).create(vals)

        purchase_request_line._compute_purchase_state()
        # Error case purchase_order in state done
        with self.assertRaisesRegex(UserError, "has already been completed"):
            purchase.button_confirm()
        purchase.button_cancel()
        self.assertEqual(purchase.state, "cancel")
        purchase_request_line._compute_purchase_state()
        with self.assertRaisesRegex(
            exceptions.UserError,
            "You cannot delete a purchase request which is not draft",
        ):
            purchase_request.unlink()
        purchase_request.button_draft()
        purchase_request.unlink()

    def test_auto_reject(self):
        """Tests if a Purchase Request is autorejected when all lines are
        cancelled."""
        purchase_request = self.purchase_request
        # Add a second line to the PR:
        vals = {
            "request_id": purchase_request.id,
            "product_id": self.env.ref("product.product_product_16").id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 5.0,
        }
        self.purchase_request_line_obj.create(vals)
        lines = purchase_request.line_ids
        # Cancel one line:
        lines[0].do_cancel()
        self.assertNotEqual(
            purchase_request.state,
            "rejected",
            "Purchase Request should not have been rejected.",
        )
        # Cancel the second one:
        lines[1].do_cancel()
        self.assertEqual(
            purchase_request.state,
            "rejected",
            "Purchase Request should have been auto-rejected.",
        )

    def test_pr_line_to_approve_allowed(self):
        request = self.purchase_request
        self.assertTrue(request.to_approve_allowed)

        pr_lines = self.purchase_request.line_ids
        pr_lines.write({"product_qty": 0})
        self.assertFalse(request.to_approve_allowed)

        pr_lines.write({"product_qty": 5})
        self.assertTrue(request.to_approve_allowed)

        pr_lines.do_cancel()
        self.assertFalse(request.to_approve_allowed)

        # Request has been automatically rejected
        request.button_draft()
        new_line = self.purchase_request_line_obj.create(
            {
                "product_id": self.env.ref("product.product_product_16").id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "product_qty": 0.0,
                "request_id": request.id,
            }
        )
        pr_lines.do_cancel()
        self.assertFalse(request.to_approve_allowed)

        new_line.write({"product_qty": 1})
        self.assertTrue(request.to_approve_allowed)
        request.line_ids.unlink()
        self.assertFalse(request.to_approve_allowed)

    def test_empty_purchase_request(self):
        pr = self.purchase_request
        pr_lines = pr.line_ids
        pr_lines.write({"product_qty": 0})

        with self.assertRaises(UserError):
            self.purchase_request.button_to_approve()

        pr_lines.write({"product_qty": 4})
        pr.button_to_approve()
        self.assertEqual(pr.state, "to_approve")

    def test_default_picking_type(self):
        with Form(self.purchase_request_obj) as f:
            f.name = "Test Purchase"
            f.requested_by = self.env.user
        f.save()

    def test_copy_purchase_request(self):
        purchase_request = self.purchase_request
        # Add a second line to the PR:
        vals = {
            "request_id": purchase_request.id,
            "product_id": self.env.ref("product.product_product_16").id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 5.0,
        }
        self.purchase_request_line_obj.create(vals)
        purchase_request_copy = purchase_request.copy()
        self.assertEqual(purchase_request_copy.state, "draft")

    def test_raise_error(self):
        vals = {
            "picking_type_id": self.env.ref("stock.picking_type_in").id,
            "requested_by": SUPERUSER_ID,
        }
        purchase_request = self.purchase_request.create(vals)
        vals = {
            "request_id": purchase_request.id,
            "product_id": self.env.ref("product.product_product_16").id,
            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
            "product_qty": 2.0,
        }
        purchase_request_line = self.purchase_request_line_obj.create(vals)
        self.assertEqual(purchase_request.state, "draft")
        # create purchase order from draft state
        with self.assertRaises(UserError):
            self.wiz.with_context(
                active_model="purchase.request.line",
                active_ids=[purchase_request_line.id],
            ).create(vals)
        purchase_request.button_done()
        # create purchase order from done state
        self.assertEqual(purchase_request.state, "done")
        purchase_request_line._compute_is_editable()
        with self.assertRaisesRegex(UserError, "already been completed"):
            self.wiz.with_context(
                active_model="purchase.request.line",
                active_ids=[purchase_request_line.id],
            ).create(vals)
        # Change product_qty to negative
        purchase_request_line.write({"product_qty": -6})
        purchase_request.button_approved()
        self.assertEqual(purchase_request.state, "approved")
        vals = {"supplier_id": self.env.ref("base.res_partner_1").id}
        wiz_id = self.wiz.with_context(
            active_model="purchase.request.line", active_ids=[purchase_request_line.id]
        ).create(vals)
        with self.assertRaisesRegex(UserError, "Enter a positive quantity"):
            wiz_id.make_purchase_order()

    def test_purchase_request_unlink(self):
        pr = self.purchase_request
        pr_lines = pr.line_ids

        pr.button_to_approve()
        self.assertEqual(pr.state, "to_approve", "Should be in state to_approve")
        with self.assertRaises(exceptions.UserError) as e:
            pr_lines.unlink()
        msg = (
            "You can only delete a purchase request line "
            "if the purchase request is in draft state."
        )
        self.assertIn(msg, e.exception.args[0])
        pr.button_done()
        self.assertEqual(pr.state, "done", "Should be in state done")
        with self.assertRaises(exceptions.UserError) as e:
            pr_lines.unlink()
        msg = (
            "You can only delete a purchase request line "
            "if the purchase request is in draft state."
        )
        self.assertIn(msg, e.exception.args[0])
        pr.button_draft()
        self.assertEqual(pr.state, "draft", "Should be in state draft")
        pr_lines.unlink()
