# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    start_lock_date = fields.Date()
    end_lock_date = fields.Date()
    block_stock_entrance = fields.Boolean(
        readonly=True,
        help="if this box is checked, putting stock on this location won't be "
        "allowed. Usually used for a virtual location that has "
        "childrens.",
    )
