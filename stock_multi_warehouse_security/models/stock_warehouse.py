# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class StockWarhouse(models.Model):
    _inherit = "stock.warehouse"

    @api.model
    def _get_available_warehouse_ids(self):
        return self.env.user.warehouse_id + self.env.user.warehouse_ids

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        context = dict(self.env.context)
        if context.pop('user_preference', None):
            warehouses = self._get_available_warehouse_ids()
            args = (args or []) + [('id', 'in', warehouses.ids)]
        return super(StockWarhouse, self.with_context(context)).\
            name_search(name=name, args=args, operator=operator, limit=limit)
