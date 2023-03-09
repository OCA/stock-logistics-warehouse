from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    pass_interchangeable = fields.Boolean()
    available_pass_interchangeable = fields.Boolean()

    @api.onchange("picking_type_id")
    def _onchange_available_pass_interchangeable(self):
        """Compute available to showing pass_interchangeable field"""
        type_ = self.picking_type_id
        self.available_pass_interchangeable = (
            type_.substitute_products_mode and type_.code == "outgoing"
        )
