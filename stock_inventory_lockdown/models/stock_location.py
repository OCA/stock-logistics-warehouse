# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    """Refuse changes during exhaustive Inventories"""
    _inherit = 'stock.location'
    _order = 'name'

    @api.multi
    @api.constrains('location_id')
    def _check_inventory_location_id(self):
        """Error if an inventory is being conducted here"""
        vals = set(self.ids) | set(self.mapped('location_id').ids)
        location_inventory_open_ids = self.env['stock.inventory'].sudo().\
            _get_locations_open_inventories(vals)
        if location_inventory_open_ids:
            raise ValidationError(
                _('An inventory is being conducted at this location'))

    @api.multi
    def unlink(self):
        """Refuse unlink if an inventory is being conducted"""
        location_inventory_open_ids = self.env['stock.inventory'].sudo().\
            _get_locations_open_inventories(self.ids)
        if location_inventory_open_ids:
            raise ValidationError(
                _('An inventory is being conducted at this location'))
        return super(StockLocation, self).unlink()
