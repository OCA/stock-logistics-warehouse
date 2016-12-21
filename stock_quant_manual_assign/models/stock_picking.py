# -*- coding: utf-8 -*-
# (c) 2015 Mikel Arregi - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_assign(self):
        # This is to assure that stock.pack.operation are reprocessed
        self.mapped('pack_operation_ids').unlink()
        return super(StockPicking, self).action_assign()


class StockMove(models.Model):
    _inherit = 'stock.move'

    picking_type_code = fields.Selection(
        related='picking_type_id.code', store=True, readonly=True)
