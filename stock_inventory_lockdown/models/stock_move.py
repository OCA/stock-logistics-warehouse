# -*- coding: utf-8 -*-
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _
from openerp.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.constrains('location_dest_id', 'location_id', 'state')
    def _check_locked_location(self):
        for move in self:
            if move.state == 'draft':
                continue
            locked_location_ids = self.env[
                'stock.inventory']._get_locations_open_inventories(
                [move.location_dest_id.id, move.location_id.id])
            if (locked_location_ids and
                    move.product_id.property_stock_inventory not in [
                        move.location_dest_id, move.location_id]):
                location_names = locked_location_ids.mapped('complete_name')
                raise ValidationError(
                    _('An inventory is being conducted at the following '
                      'location(s):\n%s') % "\n - ".join(location_names))
