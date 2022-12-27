# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    actual_date = fields.Date(related="move_id.actual_date", store=True)
