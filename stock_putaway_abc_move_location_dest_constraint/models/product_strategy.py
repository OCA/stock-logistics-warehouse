# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models
from odoo.exceptions import ValidationError


class StockPutawayRule(models.Model):

    _inherit = 'stock.putaway.rule'

    @api.multi
    def validate_abc_locations(self, locations):
        res = super().validate_abc_locations(locations)
        product = None
        if self.product_id:
            product = self.product_id
        checked_locations = self.env['stock.location']
        for loc in res:
            try:
                loc.check_move_dest_constraint(product=product)
            except ValidationError:
                continue
            checked_locations |= loc
        return checked_locations
