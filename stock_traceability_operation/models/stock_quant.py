# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from openerp.tools.translate import _


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.multi
    def action_traceability_operation(self):
        """Return an action directing to the traceability report"""
        report_obj = self.env['report.stock.traceability_operation']
        report_ids = []
        for move in self.mapped('history_ids'):
            report_vals = {'name': move.name,
                           'move_id': move.id,
                           'picking_id': move.picking_id.id,
                           'origin': move.origin,
                           'picking_type_id': move.picking_type_id.id,
                           'create_date': move.create_date,
                           'product_id': move.product_id.id,
                           #  Notice: we'll convert all to product's UoM
                           'product_uom': move.product_id.uom_id.id,
                           'product_uos_qty': move.product_uos_qty,
                           'product_uos': move.product_uos.id,
                           'date': move.date,
                           'date_expected': move.date_expected,
                           'state': move.state,
                           'partner_id': move.partner_id.id}
            # Find the pack operations linked to this move and quant
            op_links = move.linked_move_operation_ids.filtered(
                lambda l: l.reserved_quant_id in self)
            for l in op_links:
                # we report the stock move detailed by operation link
                report_vals.update(
                    {'product_uom_qty': l.qty,
                     'operation_id': l.operation_id.id,
                     'location_id': l.operation_id.location_id.id,
                     'location_dest_id': l.operation_id.location_dest_id.id})
                report_ids.append(report_obj.create(report_vals).id)
            if not op_links:
                # We report the stock move itself
                # Notice: product_qty is in the product'sUoM
                report_vals.update(
                    {'product_uom_qty': move.product_qty,
                     'location_id': move.location_id.id,
                     'location_dest_id': move.location_dest_id.id})
                report_ids.append(report_obj.create(report_vals).id)
        return {
            'domain': [('id', 'in', report_ids)],
            'name': _('Detailed traceability'),
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'report.stock.traceability_operation',
            'type': 'ir.actions.act_window',
            'context': {'search_default_done': True}}
