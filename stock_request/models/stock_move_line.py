# Copyright 2017 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def _stock_request_confirm_done_message_content(self, message_data):
        title = (
            _("Receipt confirmation %(picking_name)s for your Request %(request_name)s")
            % message_data
        )
        message = "<h3>%s</h3>" % title
        message += (
            _(
                "The following requested items from Stock Request %(request_name)s "
                "have now been received in %(location_name)s using Picking %(picking_name)s:"
            )
            % message_data
        )
        message += "<ul>"
        message += (
            _(
                "<li><b>%(product_name)s</b>: Transferred quantity %(product_qty)s"
                "%(product_uom)s</li>"
            )
            % message_data
        )
        message += "</ul>"
        return message

    def _prepare_message_data(self, ml, request, allocated_qty):
        return {
            "request_name": request.name,
            "picking_name": ml.picking_id.name,
            "product_name": ml.product_id.name_get()[0][1],
            "product_qty": allocated_qty,
            "product_uom": ml.product_uom_id.name,
            "location_name": ml.location_dest_id.name_get()[0][1],
        }

    def _action_done(self):
        res = super(StockMoveLine, self)._action_done()
        for ml in self.filtered(lambda m: m.exists() and m.move_id.allocation_ids):
            qty_done = ml.product_uom_id._compute_quantity(
                ml.qty_done, ml.product_id.uom_id
            )

            # We do sudo because potentially the user that completes the move
            #  may not have permissions for stock.request.
            to_allocate_qty = qty_done
            for allocation in ml.move_id.allocation_ids.sudo():
                allocated_qty = 0.0
                if allocation.open_product_qty:
                    allocated_qty = min(allocation.open_product_qty, to_allocate_qty)
                    allocation.allocated_product_qty += allocated_qty
                    to_allocate_qty -= allocated_qty
                if allocated_qty:
                    request = allocation.stock_request_id
                    message_data = self._prepare_message_data(
                        ml, request, allocated_qty
                    )
                    message = self._stock_request_confirm_done_message_content(
                        message_data
                    )
                    request.message_post(body=message, subtype_xmlid="mail.mt_comment")
                    request.check_done()
        return res
