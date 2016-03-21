# -*- coding: utf-8 -*-
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _
from openerp.exceptions import ValidationError


class StockLocation(models.Model):
    """Refuse changes during exhaustive Inventories"""
    _inherit = 'stock.location'
    _order = 'name'

    @api.multi
    def _check_inventory(self):
        """Error if an inventory is being conducted here"""
        location_inventory_open_ids = self.env['stock.inventory'].sudo(
            )._get_locations_open_inventories()
        for location in self:
            if location in location_inventory_open_ids:
                raise ValidationError(
                    _('An inventory is being conducted at this '
                      'location'))

    @api.multi
    def write(self, vals):
        """Refuse write if an inventory is being conducted"""
        locations_to_check = self
        # If changing the parent, no inventory must conducted there either
        if vals.get('location_id'):
            locations_to_check |= self.browse(vals['location_id'])
        locations_to_check._check_inventory()
        return super(StockLocation, self).write(vals)

    @api.model
    def create(self, vals):
        """Refuse create if an inventory is being conducted at the parent"""
        if 'location_id' in vals:
            self.browse(vals['location_id'])._check_inventory()
        return super(StockLocation, self).create(vals)

    @api.multi
    def unlink(self):
        """Refuse unlink if an inventory is being conducted"""
        self._check_inventory()
        return super(StockLocation, self).unlink()
