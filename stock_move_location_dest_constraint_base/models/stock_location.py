# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models, fields
from odoo.exceptions import ValidationError


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

    def filtered(self, func):
        """Filter locations according to installed constraints"""
        locations = super().filtered(func)
        if self.env.context.get('_filter_on_constraints'):
            product_id = self.env.context.get('_constraint_product')
            product = self.env['product.product'].browse(product_id)
            new_locations = self.browse()
            for loc in locations:
                try:
                    loc.check_move_dest_constraint(product=product)
                except ValidationError:
                    continue
                new_locations |= loc
            locations = new_locations
        return locations
