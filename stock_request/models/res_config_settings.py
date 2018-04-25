# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_stock_request_order = fields.Boolean(
        implied_group='stock_request.group_stock_request_order')

    module_stock_request_purchase = fields.Boolean(
        string='Stock Requests for Purchases')

    module_stock_request_kanban = fields.Boolean(
        string='Stock Requests Kanban integration')
