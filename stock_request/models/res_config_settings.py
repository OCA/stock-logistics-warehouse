# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_stock_request_order = fields.Boolean(
        implied_group="stock_request.group_stock_request_order"
    )

    module_stock_request_purchase = fields.Boolean(
        string="Stock Requests for Purchases"
    )

    module_stock_request_kanban = fields.Boolean(
        string="Stock Requests Kanban integration"
    )

    stock_request_check_available_first = fields.Boolean(
        related="company_id.stock_request_check_available_first", readonly=False
    )
    stock_request_allow_virtual_loc = fields.Boolean(
        related="company_id.stock_request_allow_virtual_loc", readonly=False
    )

    module_stock_request_analytic = fields.Boolean(
        string="Stock Requests Analytic integration"
    )

    module_stock_request_submit = fields.Boolean(
        string="Submitted state in Stock Requests"
    )

    module_stock_request_mrp = fields.Boolean(string="Stock Request for Manufacturing")

    # Dependencies
    @api.onchange("stock_request_allow_virtual_loc")
    def _onchange_stock_request_allow_virtual_loc(self):
        if self.stock_request_allow_virtual_loc:
            self.group_stock_multi_locations = True
