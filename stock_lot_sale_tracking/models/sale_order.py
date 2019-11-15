# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    sale_lot_tracking_ids = fields.One2many(
        comodel_name='stock.lot.sale.tracking.detail',
        string="Lot Tracking Detail",
        inverse_name='order_id'
    )
    sale_lot_tracking_count = fields.Integer(
        compute='_compute_sale_lot_tracking_count',
    )

    @api.multi
    def action_view_lot_tracking_detail(self):
        self.ensure_one()
        ref = 'stock_lot_sale_tracking.action_stock_lot_sale_detail_from_sale'
        sale_id = self.id
        action_dict = self.env.ref(ref).read()[0]
        action_dict['domain'] = [('order_id', '=', sale_id)]
        return action_dict

    @api.multi
    @api.depends('sale_lot_tracking_ids')
    def _compute_sale_lot_tracking_count(self):
        for sale in self:
            sale.sale_lot_tracking_count = len(sale.sale_lot_tracking_ids)
