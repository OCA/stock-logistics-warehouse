# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, exceptions, fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    src_routing_location_ids = fields.One2many(
        'stock.location', 'src_routing_picking_type_id'
    )
    dest_routing_location_ids = fields.One2many(
        'stock.location', 'dest_routing_picking_type_id'
    )

    def _check_routing_location_unique(self, routing_type):
        if routing_type not in ('src', 'dest'):
            raise ValueError(
                "routing_type must be one of ('src', 'dest')"
            )
        if routing_type == 'src':
            routing_location_fieldname = "src_routing_location_ids"
            default_location_fieldname = "default_location_src_id"
            message_fragment = _("source")
        else:  # dest
            routing_location_fieldname = "dest_routing_location_ids"
            default_location_fieldname = "default_location_dest_id"
            message_fragment = _("destination")
        for picking_type in self:
            if not picking_type[routing_location_fieldname]:
                continue
            if len(picking_type[routing_location_fieldname]) > 1:
                raise exceptions.ValidationError(_(
                    'The same picking type cannot be used on different '
                    'locations having routing operations.'
                ))
            if (
                picking_type[routing_location_fieldname]
                != picking_type[default_location_fieldname]
            ):
                raise exceptions.ValidationError(_(
                    'A picking type for routing operations cannot have a'
                    ' different default %s location than the location it '
                    'is used on.'
                ) % (message_fragment,))
            default_location = picking_type[default_location_fieldname]
            domain = [
                (routing_location_fieldname, '!=', False),
                (default_location_fieldname, '=', default_location.id),
                ('id', '!=', picking_type.id)
            ]
            other = self.search(domain)
            if other:
                raise exceptions.ValidationError(
                    _('Another routing operation picking type (%s) exists for'
                      ' the same %s location.') % (other.display_name,
                                                   message_fragment)
                )

    @api.constrains(
        'src_routing_location_ids', 'default_location_src_id'
    )
    def _check_src_routing_location_unique(self):
        self._check_routing_location_unique("src")

    @api.constrains(
        'dest_routing_location_ids', 'default_location_dest_id'
    )
    def _check_dest_routing_location_unique(self):
        self._check_routing_location_unique("dest")
