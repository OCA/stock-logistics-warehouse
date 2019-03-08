# Copyright 2019 Jarsa Sistemas, www.vauxoo.com
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def _adjust_procure_method(self):
        try:
            mto_route = self.env['stock.warehouse']._find_global_route(
                'stock.route_warehouse0_mto', ('Make To Order'))
        except UserError:
            mto_route = False
        for move in self.move_raw_ids:
            qty_available = move.product_id.qty_available
            # move_qty = move.product_uom_qty
            if qty_available == 0.0:
                move.procure_method = 'make_to_order'
