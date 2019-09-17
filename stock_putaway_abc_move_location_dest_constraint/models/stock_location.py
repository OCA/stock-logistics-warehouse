# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockLocation(models.Model):

    _inherit = 'stock.location'

    def check_move_dest_constraint(self, line=None, product=None):
        # As stock.putaway.rule.location_out_id is not required when
        # stock_putaway_abc is installed, we check here that this method
        # is called on an existing stock.location to avoid error on ensure_one
        # in stock_move_location_dest_constraint_base
        if not self:
            return False
        return super().check_move_dest_constraint(line=line, product=product)
