# -*- coding: utf-8 -*-
# © 2015 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class StockProductionLot(models.Model):
    """Add the computation for the stock quantities for each lot"""
    _inherit = 'stock.production.lot'

    qty_available = fields.Float(
        compute='_get_lot_qty',
        type='float',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        string='On hand')

    @api.multi
    @api.depends('quant_ids')
    def _get_lot_qty(self):
        """Compute the quantities for production lots."""
        for lot in self:
            context = dict(self.env.context, lot_id=lot.id)
            lot.qty_available = lot.with_context(context).product_id.qty_available
