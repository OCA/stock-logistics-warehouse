# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _action_done(self):
        res = super()._action_done()
        self.mapped("location_id").check_zero_confirmation()
        return res
