# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    orderpoint_product_max_qty = fields.Integer(
        'Max. product quantity',
        help='Default orderpoint Max. product quantity', default=0)
    orderpoint_product_min_qty = fields.Integer(
        'Min. product quantity',
        help='Default orderpoint Max. product quantity', default=0)
    create_orderpoints = fields.Boolean(
        'Create Orderpoints', help='Check this for automatic orderpoints')

    @api.constrains('orderpoint_product_max_qty', 'orderpoint_product_min_qty')
    def _check_orderpoint_product_qty(self):
        if (self.orderpoint_product_max_qty < 0 or
                self.orderpoint_product_min_qty < 0):
            raise exceptions.Warning(
                _('Orderpoint product quantity cannot be negative'))
