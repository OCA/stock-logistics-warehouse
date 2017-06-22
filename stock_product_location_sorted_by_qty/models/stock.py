# coding: utf-8
# © 2017 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.model
    def name_search(self, name=None, args=None, operator='ilike', limit=100):
        context = self.env.context
        res = super(StockLocation, self).name_search(
            name=name, args=args, operator=operator, limit=None)
        filtered_loc_list = []
        if context.get('stock_change_product_quantity', False):
            domain = [
                ('qty', '>', 0),
                ('product_id', '=', context.get('default_product_id', False)),
                ('location_id.usage', '=', 'internal')
            ]
            quants = self.env['stock.quant'].read_group(
                domain, ['location_id', 'qty'], 'location_id',
                orderby='qty desc')
            for elm in quants:
                if elm['location_id'] in res:
                    filtered_loc_list.append(elm['location_id'])
                    index = res.index(elm['location_id'])
                    del res[index]
            res = filtered_loc_list + res
        return res

    @api.multi
    def name_get(self):
        res = super(StockLocation, self).name_get()
        if self._context.get('stock_change_product_quantity', False):
            names = []
            for elm in res:
                quants = self.env['stock.quant'].search([
                    ('location_id', '=', elm[0]),
                    ('product_id', '=', self._context.get(
                        'default_product_id', False))
                ])
                qty = 0
                for quant in quants:
                    qty += quant.qty
                names.append((elm[0], elm[1] + ' (%s)' % qty))
            res = names
        return res
