# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
"""Allow forcing reservations of quants in a location (or children)

When the context key "gather_in_location_id" is passed, it will look
in this location or its children.

Example::

    moves.with_context(
        gather_in_location_id=location.id,
    )._action_assign()

"""

from odoo import models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _update_reserved_quantity(self, product_id, location_id, quantity,
                                  lot_id=None, package_id=None, owner_id=None,
                                  strict=False):
        gather_in_location_id = self.env.context.get('gather_in_location_id')
        if gather_in_location_id:
            location_model = self.env['stock.location']
            location_id = location_model.browse(gather_in_location_id)
        result = super()._update_reserved_quantity(
            product_id, location_id, quantity, lot_id=lot_id,
            package_id=package_id, owner_id=owner_id, strict=strict,
        )
        return result

    def _update_available_quantity(self, product_id, location_id, quantity,
                                   lot_id=None, package_id=None, owner_id=None,
                                   in_date=None):
        gather_in_location_id = self.env.context.get('gather_in_location_id')
        if gather_in_location_id:
            location_model = self.env['stock.location']
            location_id = location_model.browse(gather_in_location_id)
        result = super()._update_available_quantity(
            product_id, location_id, quantity, lot_id=lot_id,
            package_id=package_id, owner_id=owner_id, in_date=in_date,
        )
        return result

    def _get_available_quantity(self, product_id, location_id, lot_id=None,
                                package_id=None, owner_id=None, strict=False,
                                allow_negative=False):
        gather_in_location_id = self.env.context.get('gather_in_location_id')
        if gather_in_location_id:
            location_model = self.env['stock.location']
            location_id = location_model.browse(gather_in_location_id)
        result = super()._get_available_quantity(
            product_id, location_id, lot_id=lot_id,
            package_id=package_id, owner_id=owner_id, strict=strict,
        )
        return result
