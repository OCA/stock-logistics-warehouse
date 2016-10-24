# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    procure_uom_id = fields.Many2one(comodel_name='product.uom',
                                     string="Procurement UoM")

    @api.constrains('product_uom', 'procure_uom_id')
    def _check_procure_uom(self):
        if any(orderpoint.product_uom and
                orderpoint.procure_uom_id and
                orderpoint.product_uom.category_id !=
                orderpoint.procure_uom_id.category_id
                for orderpoint in self):
                    raise UserError(
                        _('Error: The product default Unit of Measure and '
                          'the procurement Unit of Measure must be in the '
                          'same category.'))
        return True
