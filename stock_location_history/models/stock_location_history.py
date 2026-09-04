from odoo import fields, models


class StockLocationHistory(models.Model):
    _name = "stock.location.history"
    _description = "Stock Location History"
    _order = "date desc"

    location_id = fields.Many2one("stock.location", string="Location", required=True)
    product_id = fields.Many2one(related="lot_id.product_id", store=True)
    lot_id = fields.Many2one("stock.lot", string="Lot/Serial Number")
    previous_stage_id = fields.Many2one("stock.location.stage", string="Previous Stage")
    new_stage_id = fields.Many2one("stock.location.stage", string="New Stage")
    user_id = fields.Many2one("res.users", string="Performed by")
    date = fields.Datetime(default=fields.Datetime.now)
    registry_type = fields.Char()
