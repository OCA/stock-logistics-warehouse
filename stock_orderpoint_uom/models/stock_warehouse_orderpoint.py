# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    procure_uom_id = fields.Many2one(comodel_name='uom.uom',
                                     string="Procurement UoM")

    @api.constrains('product_id', 'procure_uom_id')
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
