from odoo import fields, models


class StockLotMacrolot(models.Model):
    _inherit = "stock.lot"

    quantity_in = fields.Float(help="Everything that has entered")
    first_ticket = fields.Char(help="First ticket name")
    date_first_ticket = fields.Date(help="First ticket date")
    last_ticket = fields.Char(help="Last ticket name")
    date_last_ticket = fields.Date(help="Last ticket date")
    quantity_difference = fields.Float(help="Quantity on hand")
    total_consumption = fields.Float(help="Total consumed")
    initial_mix = fields.Char(help="Initial mix code")
    kg_consumed_mi = fields.Float(help="Kilograms consumed from the Initial Mix")
    final_mix = fields.Char(help="Final Mix")
    kg_consumed_mf = fields.Float(help="Kilograms consumed from the Final Mix")
