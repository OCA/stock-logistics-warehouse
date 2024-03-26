# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_cancel(self):
        """We need to call the exception before canceling to have the link
        to the productions yet."""
        self._exception_on_stock_request()
        super().button_cancel()

    def _get_exception_on_stock_request_info(self):
        """Obtain all purchases not cancelled and not linked to stock requests.
        Obtain the linked productions, and from them we obtain top parent."""
        res = super()._get_exception_on_stock_request_info()
        requests_info = res[0]
        request_orders_info = res[1]
        purchase_model = self.env["purchase.order"]
        for item in self.filtered(
            lambda x: x.state != "cancel" and not x.stock_request_ids
        ):
            res_productions = item.action_view_mrp_productions()
            res_model = self.env[res_productions["res_model"]].sudo()
            productions = (
                res_model.browse(res_productions["res_id"])
                if "res_id" in res_productions
                else res_model.search(res_productions["domain"])
            )
            sources = productions._get_all_sources() or productions
            for request in sources.stock_request_ids:
                if request.order_id:
                    if request.order_id not in request_orders_info:
                        request_orders_info[request.order_id] = purchase_model
                    request_orders_info[request.order_id] += item
                else:
                    if request not in requests_info:
                        requests_info[request] = purchase_model
                    requests_info[request] += item
        return requests_info, request_orders_info
