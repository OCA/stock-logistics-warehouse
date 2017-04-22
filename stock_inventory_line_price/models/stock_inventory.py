# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def _get_inventory_lines(self, inventory):
        vals = super(StockInventory, self)._get_inventory_lines(inventory)
        for line in vals:
            product = self.env['product.product'].browse(line['product_id'])
            line.update({'theoretical_std_price': product.standard_price,
                         'standard_price': product.standard_price})
        return vals
