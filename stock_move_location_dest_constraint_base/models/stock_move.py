# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class StockMoveLine(models.Model):

    _inherit = 'stock.move.line'

    @api.constrains('location_dest_id')
    def _check_location_dest_id(self):
        """Check if destination location is allowed"""
        for line in self:
            if line.location_dest_id.bypass_constraints:
                continue
            line.location_dest_id.check_move_dest_constraint(line=line)
