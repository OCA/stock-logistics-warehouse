# Copyright 2019 Jarsa Sistemas, www.vauxoo.com
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def _adjust_procure_method(self):
        self.invalidate_cache()
        try:
            mto_route = self.env['stock.warehouse']._find_global_route(
                'stock.route_warehouse0_mto', _('Make To Order'))
        except UserError:
            mto_route = False
        for move in self.move_raw_ids:
            product = move.product_id
            routes = (
                product.route_ids +
                product.route_from_categ_ids +
                move.warehouse_id.route_ids)
            # TODO: optimize with read_group?
            pull = self.env['stock.rule'].search([
                ('route_id', 'in', [x.id for x in routes]),
                ('location_src_id', '=', move.location_id.id),
                ('location_id', '=', move.location_dest_id.id),
                ('action', '!=', 'push')], limit=1, order='sequence asc')
            if pull and pull.action == 'split_procurement':
                qty_available = (
                    self.env['stock.quant']._get_available_quantity(
                        product_id=product, location_id=move.location_id))
                move_qty = move.product_qty
                if qty_available == 0.0:
                    move.procure_method = 'make_to_order'
                elif move_qty > qty_available and qty_available != 0.0 and qty_available > 0.001:
                    rounding_method = self._context.get(
                        'rounding_method', 'UP')
                    qty_mto = move.product_uom._compute_quantity(
                        move_qty - qty_available, product.uom_id,
                        rounding_method=rounding_method)
                    qty_mts = move.product_uom._compute_quantity(
                        qty_available, product.uom_id,
                        rounding_method=rounding_method)
                    move.copy({
                        'product_uom_qty': qty_mto,
                        'procure_method': 'make_to_order'})
                    move.product_uom_qty = qty_mts
                elif qty_available < 0.001:
                    move.procure_method = 'make_to_order'
            elif pull and (pull.procure_method == 'make_to_order'):
                move.procure_method = pull.procure_method
            elif not pull:  # If there is no make_to_stock rule either
                if mto_route and mto_route.id in [x.id for x in routes]:
                    move.procure_method = 'make_to_order'
        moves_in_zero = self.move_raw_ids.filtered(
            lambda m: m.product_uom_qty == 0.0)
        if moves_in_zero:
            moves_in_zero.write({'state': 'draft'})
            moves_in_zero.unlink()


    @api.multi
    def _update_unit_factor(self):
        self.ensure_one()
        for product in self.move_raw_ids.mapped('product_id'):
            moves = self.move_raw_ids.filtered(
                lambda m: m.product_id == product)
            if len(moves) > 1:
                for move in moves:
                    # We change the unit factor in onder to compute correctly
                    # the quantity to be processed for each stock.move
                    move.unit_factor = move.product_qty / self.product_qty

    @api.model
    def create(self, values):
        res = super().create(values)
        res._update_unit_factor()
        return res

    @api.multi
    def _update_raw_move(self, bom_line, line_data):
        res = super()._update_raw_move(bom_line, line_data)
        self._update_unit_factor()
        return res

    @api.multi
    def _generate_moves(self):
        res = super()._generate_moves()
        for production in self:
            move_mts = production.move_raw_ids.filtered(
                lambda m: m.procure_method == 'make_to_stock')
            if move_mts:
                qty_wizard = self.env['change.production.qty'].create({
                    'mo_id': production.id,
                    'product_qty': production.product_qty,
                })
                qty_wizard.change_prod_qty()
        return res
