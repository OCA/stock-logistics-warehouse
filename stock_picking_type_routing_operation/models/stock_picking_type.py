# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, exceptions, fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    src_routing_location_ids = fields.One2many(
        'stock.location', 'src_routing_picking_type_id'
    )

    @api.constrains(
        'src_routing_location_ids', 'default_location_src_id'
    )
    def _check_src_routing_location_unique(self):
        for picking_type in self:
            if not picking_type.src_routing_location_ids:
                continue
            if len(picking_type.src_routing_location_ids) > 1:
                raise exceptions.ValidationError(_(
                    'The same picking type cannot be used on different '
                    'locations having routing operations.'
                ))
            if (
                picking_type.src_routing_location_ids
                != picking_type.default_location_src_id
            ):
                raise exceptions.ValidationError(_(
                    'A picking type for routing operations cannot have a'
                    ' different default source location than the location it '
                    'is used on.'
                ))
            src_location = picking_type.default_location_src_id
            domain = [
                ('src_routing_location_ids', '!=', False),
                ('default_location_src_id', '=', src_location.id),
                ('id', '!=', picking_type.id)
            ]
            other = self.search(domain)
            if other:
                raise exceptions.ValidationError(
                    _('Another routing operation picking type (%s) exists for'
                      ' the same source location.') % (other.display_name,)
                )
