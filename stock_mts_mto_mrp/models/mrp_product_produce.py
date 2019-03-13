# Copyright 2019 Jarsa Sistemas, www.vauxoo.com
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_compare, float_round


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        lines = []
        qty_todo = self.product_uom_id._compute_quantity(
            self.product_qty, self.production_id.product_uom_id, round=False)
        for move in self.production_id.move_raw_ids.filtered(
                lambda m: m.state not in ('done', 'cancel') and m.bom_line_id):

            qty_to_consume = float_round(
                qty_todo * move.unit_factor,
                precision_rounding=move.product_uom.rounding)
            for move_line in move.move_line_ids:
                if float_compare(
                        qty_to_consume, 0.0,
                        precision_rounding=move.product_uom.rounding) <= 0:
                    break
                if move_line.lot_produced_id or float_compare(
                        move_line.product_uom_qty, move_line.qty_done,
                        precision_rounding=move.product_uom.rounding) <= 0:
                    continue
                to_consume_in_line = min(
                    qty_to_consume, move_line.product_uom_qty)
                lines.append({
                    'move_id': move.id,
                    'qty_to_consume': to_consume_in_line,
                    'qty_done': to_consume_in_line,
                    'lot_id': move_line.lot_id.id,
                    'product_uom_id': move.product_uom.id,
                    'product_id': move.product_id.id,
                    'qty_reserved': min(
                        to_consume_in_line, move_line.product_uom_qty),
                })
                qty_to_consume -= to_consume_in_line

            # TODO. Check the functionality of the code below, because
            # currently, is making double lines
            # when is usted make to order + make to stock.

            # if float_compare(
            #   qty_to_consume, 0.0,
            #   precision_rounding=move.product_uom.rounding) > 0:
            #     if move.product_id.tracking == 'serial':
            #         while float_compare(qty_to_consume, 0.0,
            #               precision_rounding=move.product_uom.rounding) > 0:
            #             lines.append({
            #                 'move_id': move.id,
            #                 'qty_to_consume': 1,
            #                 'qty_done': 1,
            #                 'product_uom_id': move.product_uom.id,
            #                 'product_id': move.product_id.id,
            #             })
            #             qty_to_consume -= 1
            #     else:
            #         lines.append({
            #             'move_id': move.id,
            #             'qty_to_consume': qty_to_consume,
            #             'qty_done': qty_to_consume,
            #             'product_uom_id': move.product_uom.id,
            #             'product_id': move.product_id.id,
            #         })
        self.produce_line_ids = [(0, 0, x) for x in lines]
