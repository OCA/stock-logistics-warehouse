from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    pass_interchangeable = fields.Boolean()
    available_pass_interchangeable = fields.Boolean()

    @api.onchange("picking_type_id")
    def _onchange_available_pass_interchangeable(self):
        """Compute available pass interchangeable field."""
        picking_type_id = self.picking_type_id

        self.available_pass_interchangeable = (
            picking_type_id.substitute_products_mode
            and picking_type_id.code == "outgoing"
        )
