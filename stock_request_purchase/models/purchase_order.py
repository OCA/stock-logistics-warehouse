# Copyright 2017-20 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    stock_request_ids = fields.Many2many(
        comodel_name="stock.request",
        string="Stock Requests",
        compute="_compute_stock_request_ids",
    )
    stock_request_count = fields.Integer(
        "Stock Request #", compute="_compute_stock_request_ids"
    )

    @api.depends("order_line")
    def _compute_stock_request_ids(self):
        for rec in self:
            rec.stock_request_ids = rec.order_line.mapped("stock_request_ids")
            rec.stock_request_count = len(rec.stock_request_ids)

    def button_cancel(self):
        super().button_cancel()
        self._exception_on_stock_request()

    def _get_exception_on_stock_request_info(self):
        requests_info = {}
        request_orders_info = {}
        purchase_model = self.env["purchase.order"]
        for item in self.filtered(
            lambda x: x.state == "cancel" and x.stock_request_ids
        ):
            for request in item.stock_request_ids:
                if request.order_id:
                    if request.order_id not in request_orders_info:
                        request_orders_info[request.order_id] = purchase_model
                    request_orders_info[request.order_id] += item
                else:
                    if request not in requests_info:
                        requests_info[request] = purchase_model
                    requests_info[request] += item
        return requests_info, request_orders_info

    def _exception_on_stock_request(self):
        """Group by stock.request or stock.request.order with all orders."""

        def _render_note_exception_request(rendering_context):
            item = rendering_context[0]
            key = item._name.replace(".", "_")
            values = {
                "orders": rendering_context[1],
                key: item,
            }
            template = self.env.ref("stock_request_purchase.exception_po_cancel")
            return template._render(values=values)

        requests_info, request_orders_info = self._get_exception_on_stock_request_info()
        picking_model = self.env["stock.picking"]
        # stock.request
        for request, purchase_orders in requests_info.items():
            documents = {(request, self.env.user): (request, purchase_orders)}
            picking_model._log_activity(_render_note_exception_request, documents)
        # stock.request.order
        for order, purchase_orders in request_orders_info.items():
            documents = {(order, self.env.user): (order, purchase_orders)}
            picking_model._log_activity(_render_note_exception_request, documents)

    def _get_stock_requests(self):
        """Get all stock requests from action (allows inheritance by other modules)."""
        return self.mapped("stock_request_ids")

    def action_view_stock_request(self):
        """
        :return dict: dictionary value for created view
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_request.action_stock_request_form"
        )

        requests = self._get_stock_requests()
        if len(requests) > 1:
            action["domain"] = [("id", "in", requests.ids)]
        elif requests:
            action["views"] = [
                (self.env.ref("stock_request.view_stock_request_form").id, "form")
            ]
            action["res_id"] = requests.id
        return action
