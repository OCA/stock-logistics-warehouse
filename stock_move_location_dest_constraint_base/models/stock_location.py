# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models, fields


class StockLocation(models.Model):

    _inherit = 'stock.location'

    bypass_constraints = fields.Boolean()

    def check_move_dest_constraint(self, line=None, product=None):
        """Raise Validation error if not allowed"""
        self.ensure_one()
        return True

    @api.model
    def _set_bypass_on_existing_locations(self):
        """Set bypass_constrains on all the existing locations"""
        existing_locations = self.search([])
        existing_locations.write({'bypass_constraints': True})

    def get_putaway_strategy(self, product):
        """Activate constraint when looking for putaway rules"""
        self = self.with_context(
            _filter_on_constraints=True, _constraint_product=product.id
        )
        return super().get_putaway_strategy(product)
