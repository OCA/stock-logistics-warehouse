# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockRoute(models.Model):
    _inherit = "stock.route"

    is_mto = fields.Boolean(
        help="Is a MTO (Make to Order) route. Check this if you want to identify"
        "this route as an MTO one."
    )
