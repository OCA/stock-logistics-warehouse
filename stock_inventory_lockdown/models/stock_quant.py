# -*- coding: utf-8 -*-
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _
from openerp.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    def write(self, vals):
        """Check that the location is not locked by an open inventory.
        Check both the location as it was (source) and the location as
        it will be (destination).
        We verify the locations even if they are unchanged, because changing
        ie. the quantity is not acceptable either.
        @raise ValidationError if they are.
        """
        if not self.env.context.get('bypass_lockdown', False):
            # Find the locked locations
            locked_location_ids = self.env[
                'stock.inventory']._get_locations_open_inventories()
            if locked_location_ids and 'location_id' in vals.keys():
                messages = set()
                # Find the destination locations
                location_dest_id = self.env['stock.location'].browse(
                    vals['location_id'])
                for quant in self:
                    # Source locations
                    location_id = quant.location_id
                    # Moving to a location locked down
                    if location_dest_id in locked_location_ids:
                        messages.add(location_dest_id.name)
                    # Moving from a location locked down
                    if location_id in locked_location_ids:
                        messages.add(location_id.name)
                if len(messages):
                    raise ValidationError(
                        _('An inventory is being conducted at the following '
                          'location(s):\n%s') % "\n - ".join(messages))
        return super(StockQuant, self).write(vals)

    @api.model
    def create(self, vals):
        """Check that the locations are not locked by an open inventory.
        @raise ValidationError if they are.
        """
        quant = super(StockQuant, self).create(vals)
        if not self.env.context.get('bypass_lockdown', False):
            locked_location_ids = self.env[
                'stock.inventory']._get_locations_open_inventories()
            if quant.location_id in locked_location_ids:
                raise ValidationError(
                    _('An inventory is being conducted at the following '
                      'location(s):\n%s') % " - " + quant.location_id.name)
        return quant
