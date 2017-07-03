# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare


class ResCompany(models.Model):
    _inherit = 'res.company'

    orderpoint_product_max_qty = fields.Float(
        string='Max. product quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        help='Default orderpoint Max. product quantity',
    )
    orderpoint_product_min_qty = fields.Float(
        string='Min. product quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        help='Default orderpoint Max. product quantity',
    )
    create_orderpoints = fields.Boolean(
        string='Create Orderpoints',
        help='Check this for automatic orderpoints',
    )

    @api.multi
    @api.constrains('orderpoint_product_max_qty', 'orderpoint_product_min_qty')
    def _check_orderpoint_product_qty(self):
        for company in self:
            if float_compare(company.orderpoint_product_max_qty, 0.0,
                             2) < 0 or float_compare(
                    company.orderpoint_product_min_qty, 0.0, 2) < 0:
                raise ValidationError(
                    _('Orderpoint product quantity cannot be negative'))
