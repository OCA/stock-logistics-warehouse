from odoo import fields, models


class StockLocationHistory(models.Model):
    _name = "stock.location.history"
    _description = "Stock Location History"
    _order = "registry_date desc"

    location_id = fields.Many2one("stock.location", string="Location", required=True)
    previous_stage_id = fields.Many2one("stock.location.stage", string="Previous Stage")
    next_stage_id = fields.Many2one("stock.location.stage", string="Next Stage")
    user_id = fields.Many2one("res.users", string="Performed by")
    date = fields.Datetime(default=fields.Datetime.now)
