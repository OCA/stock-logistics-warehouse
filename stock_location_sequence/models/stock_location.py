from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"
    _order = "sequence, name"

    sequence = fields.Integer()
