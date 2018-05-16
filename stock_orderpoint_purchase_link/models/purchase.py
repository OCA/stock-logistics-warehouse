# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    @api.depends("product_id", "product_qty", "move_dest_ids")
    def _compute_orderpoint_id(self):
        for rec in self:
            orderpoint_id = rec.orderpoint_id
            warehouse = rec.order_id.picking_type_id.warehouse_id
            # Check warehouse configuration steps for incoming shipments
            if warehouse and not orderpoint_id:
                # Set orderpoint for 1 steps
                if warehouse.reception_steps == 'one_step':
                    orderpoint_id = \
                        self.env['stock.warehouse.orderpoint'].\
                        search([('product_id', '=', rec.product_id.id),
                                ('name', '=', rec.order_id.origin)], limit=1)
                # Set orderpoint for 2 steps
                elif warehouse.reception_steps == 'two_steps':
                    if rec.move_dest_ids:
                        orderpoint_id = \
                            self.env['stock.warehouse.orderpoint'].search(
                                [('product_id', '=', rec.product_id.id),
                                 ('name', '=', rec.move_dest_ids[0].origin)],
                                limit=1)
                # Set orderpoint for 3 steps
                elif warehouse.reception_steps == 'three_steps':
                    if rec.move_dest_ids:
                        orderpoint_id = \
                            self.env['stock.warehouse.orderpoint'].search(
                                [('product_id', '=', rec.product_id.id),
                                 ('name', '=',
                                  rec.move_dest_ids[0].move_dest_ids[0].origin)
                                 ], limit=1)
            rec.orderpoint_id = orderpoint_id

    orderpoint_id = fields.Many2one(
        comodel_name='stock.warehouse.orderpoint',
        compute='_compute_orderpoint_id',
        store=True,
        index=True,
        readonly=True,
    )
