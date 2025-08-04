from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    allowed_location_ids = fields.Many2many(
        "stock.location",
        compute="_compute_allowed_locations",
        store=False,
        string="Allowed Locations",
        help="Allowed locations for this product",
    )

    @api.depends("product_id")
    def _compute_allowed_locations(self):
        for line in self:
            if line.product_id and line.product_id.allowed_location_ids:
                line.allowed_location_ids = line.product_id.allowed_location_ids
            else:
                line.allowed_location_ids = self.env["stock.location"].search(
                    [("usage", "=", "internal"), ("active", "=", True)]
                )
