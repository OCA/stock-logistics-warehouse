# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# Copyright 2019 Aleph Objects, Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.multi
    def write(self, vals):
        forced_inventory_date = self.env.context.get(
            'forced_inventory_date', False)
        if 'date' in vals and forced_inventory_date:
            vals['date'] = forced_inventory_date
        return super(StockMoveLine, self).write(vals)

    @api.model
    def create(self, vals):
        forced_inventory_date = self.env.context.get(
            'forced_inventory_date', False)
        if 'date' in vals and forced_inventory_date:
            vals['date'] = forced_inventory_date
        return super(StockMoveLine, self).create(vals)
