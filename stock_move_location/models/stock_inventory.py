# Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _, fields, models
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def _select_inventory_type(self):
        return [
            ('normal', 'Inventory'),
            ('move', 'Location Move'),
        ]

    inventory_type = fields.Selection(
        string='Type',
        selection="_select_inventory_type",
        default='normal',
    )
    destination_location_id = fields.Many2one(
        string='Destination Location',
        comodel_name='stock.location',
    )
    comments = fields.Text(
        string='Comments',
    )

    def move_stock(self):
        for inventory in self:
            if not inventory.destination_location_id:
                raise ValidationError(
                    _('Please select the destination of your move')
                )
            moves = [
                (0, 0, line._get_move_location_values())
                for line in inventory.line_ids
            ]
            self.write({
                'move_ids': moves,
            })
            self.mapped('move_ids')._action_done()
            self.write({
                "state": "done",
            })
            _logger.info("Move '{}' is done.".format(inventory.name))
        return True
