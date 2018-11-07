# -*- coding: utf-8 -*-
# Copyright 2018 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super(StockLocation, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
        ordered_loc_list = []
        if self.env.context.get('stock_change_product_quantity'):
            domain = [
                ('product_id', '=', self.env.context.get(
                    'default_product_id', False)),
                ('location_id.usage', '=', 'internal')
            ]
            if self.env.context.get('default_lot_id'):
                domain += [('lot_id', '=', self.env.context.get(
                    'default_lot_id'))]
            quants = self.env['stock.quant'].read_group(
                domain, ['location_id', 'qty'], 'location_id',
                orderby='qty desc')
            for elm in quants:
                ordered_loc_list.append(elm['location_id'])
                if elm['location_id'] in res:
                    res.remove(elm['location_id'])
            res = ordered_loc_list + res
        return res

    @api.multi
    def name_get(self):
        res = super(StockLocation, self).name_get()
        if self.env.context.get('stock_change_product_quantity'):
            new_res = []
            ordered_name_loc_list = []
            domain = [
                ('product_id', '=', self.env.context.get(
                    'default_product_id', False)),
                ('location_id', 'in', self.ids)
            ]
            if self.env.context.get('default_lot_id'):
                domain += [('lot_id', '=', self.env.context.get(
                    'default_lot_id'))]
            quants = self.env['stock.quant'].with_context(
                stock_change_product_quantity=False).read_group(
                    domain, ['location_id', 'qty'], 'location_id',
                    orderby='qty desc')
            for quant in quants:
                full_name_loc = (
                    quant['location_id'][0],
                    quant['location_id'][1] + ' (%s)' % quant['qty'])
                ordered_name_loc_list.append(full_name_loc)
                if quant['location_id'] in res:
                    res.remove(quant['location_id'])
            for elm in res:
                new_res.append((elm[0], elm[1] + ' (0)'))
            res = ordered_name_loc_list + new_res
        return res
