# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockChangeProductQty(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    @api.onchange('preset_reason_id')
    def _onchange_preset_reason_id(self):
        for wizard in self:
            if wizard.preset_reason_id:
                if wizard.preset_reason_id.virtual_location_id:
                    wizard.virtual_location_id = \
                        wizard.preset_reason_id.virtual_location_id
