# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class PutAwayStrategy(models.Model):
    _inherit = 'product.putaway'

    def _get_putaway_rule(self, product):
        """Activate constraint when looking for putaway rules"""
        self = self.with_context(
            _filter_on_constraints=True, _constraint_product=product.id
        )
        return super()._get_putaway_rule(product)
