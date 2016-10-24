# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    procure_uom_id = fields.Many2one(comodel_name='product.uom',
                                     string="Procurement UoM")

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.procure_uom_id = rec.product_id.uom_id
