# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ChangeProductionQty(models.TransientModel):
    _inherit = 'change.production.qty'

    @api.multi
    def change_prod_qty(self):
        move_orig = self.mo_id.move_raw_ids[0].move_orig_ids
        moves = self.mo_id.mapped('move_raw_ids').filtered(
            lambda m: m.procure_method == 'make_to_order')
        move_lines = moves.mapped('move_line_ids')
        moves.write({
            'state': 'draft',
        })
        move_lines.write({
            'state': 'draft',
        })
        moves.unlink()
        res = super().change_prod_qty()
        # If a MTO move was deleted, the method change_prod_qty creates a new
        # move for the component, but it's in draft state and cannot be
        # reserved, we need to confirm the stock.move 
        moves = self.mo_id.move_raw_ids.filtered(
            lambda l: l.state == 'draft')._action_confirm()
        production = self.mo_id
        production.action_assign()
        done_moves = production.move_finished_ids.filtered(
            lambda x: x.state == 'done' and x.product_id ==
            production.product_id)
        qty_produced = production.product_id.uom_id._compute_quantity(
            sum(done_moves.mapped('product_qty')), production.product_uom_id)
        factor = production.product_uom_id._compute_quantity(
            production.product_qty - qty_produced,
            production.bom_id.product_uom_id) / production.bom_id.product_qty
        boms, lines = production.bom_id.explode(
            production.product_id, factor,
            picking_type=production.bom_id.picking_type_id)
        documents = {}
        picking_obj = self.env['stock.picking']
        move = self.mo_id.move_raw_ids
        for line, line_data in lines:
            if move:
                move = move[0]
                move.move_orig_ids = move_orig
                old_qty = move.product_uom_qty - move.reserved_availability
            else:
                old_qty = 0
            iterate_key = production._get_document_iterate_key(move)
            if iterate_key:
                document = picking_obj._log_activity_get_documents(
                    {move: (line_data['qty'], old_qty)}, iterate_key, 'UP')
                for key, value in document.items():
                    if documents.get(key):
                        documents[key] += [value]
                    else:
                        documents[key] = [value]
        production._log_manufacture_exception(documents)
        for move_raw in production.move_raw_ids:
            move_raw.move_orig_ids = False
        return res
