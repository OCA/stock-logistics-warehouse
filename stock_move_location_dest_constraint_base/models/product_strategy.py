# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models
from odoo.exceptions import ValidationError


class StockPutawayRule(models.Model):
    _inherit = 'stock.putaway.rule'

    def filtered(self, func):
        """Filter putaway strats according to installed constraints"""
        putaway_rules = super().filtered(func)
        if self.env.context.get('_filter_on_constraints'):
            product_id = self.env.context.get('_constraint_product')
            product = self.env['product.product'].browse(product_id)
            filtered_putaways = self.browse()
            for put in putaway_rules:
                try:
                    put.location_out_id.check_move_dest_constraint(
                        product=product
                    )
                except ValidationError:
                    continue
                filtered_putaways |= put
            putaway_rules = filtered_putaways
        return putaway_rules
