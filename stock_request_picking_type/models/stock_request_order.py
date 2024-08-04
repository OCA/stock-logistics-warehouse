# Copyright 2019 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Operation Type",
        compute="_compute_picking_type_id",
        required=True,
        store=True,
        readonly=False,
        precompute=True,
    )

    @api.depends("warehouse_id")
    def _compute_picking_type_id(self):
        for order in self:
            order.picking_type_id = order.warehouse_id.stock_request_type_id.id
            if not order.picking_type_id:
                order.message_post(body="No se encontró un tipo de operación 'stock_request_order' para el almacén '%s'." % order.warehouse_id.name)
