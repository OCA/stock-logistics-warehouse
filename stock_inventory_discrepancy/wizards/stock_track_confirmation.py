from odoo import models


class StockTrackConfirmation(models.TransientModel):
    _inherit = "stock.track.confirmation"

    def action_confirm(self):
        self = self.with_context(skip_apply_inventory=False)
        return super().action_confirm()
