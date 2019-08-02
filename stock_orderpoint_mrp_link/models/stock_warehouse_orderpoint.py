# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.multi
    def action_view_mrp_productions(self):
        action = self.env.ref('mrp.mrp_production_action')
        result = action.read()[0]
        result['context'] = {}
        mrp_production_ids = self.env['mrp.production'].search(
            [('orderpoint_id', '=', self.id)])
        result['domain'] = "[('id','in',%s)]" % mrp_production_ids.ids
        return result
