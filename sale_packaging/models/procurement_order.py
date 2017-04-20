# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    product_packaging = fields.Many2one(
        'product.packaging',
        string='Packaging',
        default=False)

    def _get_stock_move_values(self):
        vals = super(ProcurementOrder, self)._get_stock_move_values()
        if self.product_packaging:
            vals.update({'product_packaging': self.product_packaging.id})
        return vals
