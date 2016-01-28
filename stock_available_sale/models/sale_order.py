# -*- coding: utf-8 -*-
# © 2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class SaleOrder(models.Model):
    """ Add field potential_quantity on sale order form view  """
    _inherit = 'sale.order.line'

    immediately_usable_qty = fields.Float(
        related='product_id.immediately_usable_qty',
        store=False)
