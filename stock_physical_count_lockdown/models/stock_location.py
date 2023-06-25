# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    is_physical_count_lockdown = fields.Boolean(
        help="if this box is checked, putting stock on this location won't be "
        "allowed. Usually used for a virtual location that has "
        "childrens.",
    )
