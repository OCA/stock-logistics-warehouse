# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    def _get_inventory_lines_values(self):
        vals = super(StockInventory, self)._get_inventory_lines_values()
        for line in vals:
            product = self.env['product.product'].browse(line['product_id'])
            line.update({'theoretical_std_price': product.standard_price,
                         'standard_price': product.standard_price})
        return vals
