# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.multi
    def action_view_stock_picking(self):
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]
        result['context'] = {}
        picking_ids = self.env['stock.move'].search(
            [('orderpoint_ids', 'in', self.id)]).mapped('picking_id')
        result['domain'] = "[('id','in',%s)]" % picking_ids.ids
        return result
