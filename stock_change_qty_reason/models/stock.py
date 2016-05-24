# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    @api.model
    def _resolve_inventory_line(self, inventory_line):

        move_id = super(StockInventoryLine,
                        self)._resolve_inventory_line(inventory_line)

        reason = self.env.context.get('change_quantity_reason', False)
        if reason and move_id:
            move = self.env['stock.move'].browse(move_id)

            if move.origin:
                move.origin = ' ,'.join([move.origin, reason])
            else:
                move.origin = reason

        return move_id
