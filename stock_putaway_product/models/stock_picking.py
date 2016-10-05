# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _prepare_pack_ops(self, picking, quants, forced_qties):
        res = super(StockPicking, self)._prepare_pack_ops(
            picking, quants, forced_qties)
        new_res = []
        Location = self.env['stock.location']
        locations_putaway = Location.search(
            [('putaway_strategy_id', '!=', False)])
        for operation_vals in res:
            location_dest = Location.browse(operation_vals['location_dest_id'])
            if location_dest not in locations_putaway:
                new_res.append(operation_vals)
                continue
            product_id = operation_vals['product_id']
            putaway_strategy = location_dest.putaway_strategy_id
            if putaway_strategy.method == 'per_product':
                strategy_domain = [
                    ('putaway_id', '=', putaway_strategy.id),
                    ('product_product_id', '=', product_id),
                ]
                qty = operation_vals['product_qty']
                for strategy in putaway_strategy.product_location_ids.search(
                        strategy_domain):
                    new_location_dest_id = strategy.fixed_location_id.id
                    if not strategy.max_qty:
                        new_res.append(dict(
                            operation_vals,
                            location_dest_id=new_location_dest_id))
                        qty = 0.0
                        break
                    else:
                        quant_data = self.env['stock.quant'].read_group(
                            [('product_id', '=', product_id),
                             ('location_id', '=', new_location_dest_id)],
                            ['product_id', 'location_id', 'qty'],
                            ['product_id']
                        )[:1]
                        free_space = strategy.max_qty - (
                            quant_data and quant_data[0]['qty'] or 0.0)
                        if free_space <= 0.0:
                            continue
                        if free_space >= qty:
                            new_res.append(dict(
                                operation_vals,
                                product_qty=qty,
                                location_dest_id=new_location_dest_id))
                            qty = 0.0
                            break
                        else:
                            new_res.append(dict(
                                operation_vals,
                                product_qty=free_space,
                                location_dest_id=new_location_dest_id))
                            qty -= free_space
                if qty:
                    new_res.append(dict(
                        operation_vals,
                        product_qty=qty,
                        location_dest_id=location_dest.id))
        return new_res
