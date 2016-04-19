# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.multi
    def action_traceability_operation(self):
        """Return an action directing to the traceability report"""
        quants = self.env['stock.quant'].search([('lot_id', 'in', self.ids)])
        return quants.action_traceability_operation()
