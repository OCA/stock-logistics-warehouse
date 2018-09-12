# © 2016 Numérigraphe SARL
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _get_reserved_locations(self):
        self.ensure_one()
        return self.move_line_ids.mapped('location_id')

    @api.multi
    def _get_dest_locations(self):
        self.ensure_one()
        return self.move_line_ids.mapped('location_dest_id')

    @api.constrains('location_dest_id', 'location_id', 'state')
    def _check_locked_location(self):
        for move in self.filtered(lambda m: m.state != 'draft'):
            locked_location_ids = self.env[
                'stock.inventory']._get_locations_open_inventories(
                [move.location_dest_id.id, move.location_id.id])
            reserved_locs = move._get_reserved_locations()
            dest_locs = move._get_dest_locations()
            if (locked_location_ids and
                    move.product_id.property_stock_inventory not in [
                        move.location_dest_id, move.location_id] and
                    (move.location_dest_id in locked_location_ids or
                     any([l in locked_location_ids for l in dest_locs]) or
                     any([l in locked_location_ids for l in reserved_locs]))):
                location_names = locked_location_ids.mapped('complete_name')
                raise ValidationError(
                    _('An inventory is being conducted at the following '
                      'location(s):\n%s') % "\n - ".join(location_names))
