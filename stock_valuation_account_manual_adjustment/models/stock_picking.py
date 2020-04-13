# 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class Picking(models.Model):
    _inherit = "stock.picking"

    def action_view_account_moves(self):
        self.ensure_one()
        action = self.env.ref('account.action_account_moves_all_a')
        result = action.read()[0]
        result['domain'] = [('stock_move_id', 'in', self.move_lines.ids)]
        return result
