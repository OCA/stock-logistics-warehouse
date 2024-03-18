# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    stock_move_id = fields.Many2one(
        comodel_name='stock.move', string='Stock Move', copy=False,
        index=True)
