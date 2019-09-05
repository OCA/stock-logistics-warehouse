# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models
from odoo.exceptions import ValidationError


class PutAwayStrategy(models.Model):
    _inherit = 'product.putaway'

    def _get_putaway_rule(self, product):
        """Activate constraint when looking for putaway rules"""
        self = self.with_context(
            _filter_on_constraints=True, _constraint_product=product.id
        )
        return super()._get_putaway_rule(product)


class FixedPutAwayStrategy(models.Model):

    _inherit = 'stock.fixed.putaway.strat'

    def filtered(self, func):
        """Filter putaway strats according to installed constraints"""
        putaway_strats = super().filtered(func)
        if self.env.context.get('_filter_on_constraints'):
            product_id = self.env.context.get('_constraint_product')
            product = self.env['product.product'].browse(product_id)
            filtered_putaways = self.browse()
            for put in putaway_strats:
                try:
                    put.location_id.check_move_dest_constraint(product=product)
                except ValidationError:
                    continue
                filtered_putaways |= put
            putaway_strats = filtered_putaways
        return putaway_strats
