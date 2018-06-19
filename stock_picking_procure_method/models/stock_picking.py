# Copyright 2018 Tecnativa - David Vidal
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    procure_method = fields.Selection(
        selection='_selection_procure_method',
        compute='_compute_procure_method',
        inverse='_inverse_procure_method',
        string='Supply Method',
        help='By default, the system will take from the stock in the source '
             'location and passively wait for availability. The other '
             'possibility allows you to directly create a procurement on the '
             'source location (and thus ignore its current stock) to gather '
             'products. If we want to chain moves and have this one to wait '
             'for the previous, this second option should be chosen.',
    )

    def _selection_procure_method(self):
        return self.env['stock.move'].fields_get(
            allfields=['procure_method'])['procure_method']['selection']

    @api.depends('move_lines.procure_method')
    def _compute_procure_method(self):
        for picking in self:
            procure_method = False
            for move in picking.move_lines:
                if not procure_method:
                    procure_method = move.procure_method
                elif procure_method != move.procure_method:
                    procure_method = False
                    break
            picking.procure_method = procure_method

    def _inverse_procure_method(self):
        self.filtered('procure_method').mapped('move_lines').update({
            'procure_method': self.procure_method,
        })
