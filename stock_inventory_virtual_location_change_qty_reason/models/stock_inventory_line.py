# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    @api.onchange('preset_reason_id')
    def _onchange_preset_reason_id(self):
        for line in self:
            if line.preset_reason_id:
                if line.preset_reason_id.virtual_location_id:
                    line.virtual_location_id = \
                        line.preset_reason_id.virtual_location_id
