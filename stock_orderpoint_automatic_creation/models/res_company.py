# -*- coding: utf-8 -*-
# Copyright 2016 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    orderpoint_product_max_qty = fields.Integer(
        string='Max. product quantity',
        help='Default orderpoint Max. product quantity',
    )
    orderpoint_product_min_qty = fields.Integer(
        string='Min. product quantity',
        help='Default orderpoint Max. product quantity',
    )
    create_orderpoints = fields.Boolean(
        string='Create Orderpoints',
        help='Check this for automatic orderpoints',
    )

    @api.multi
    @api.constrains('orderpoint_product_max_qty', 'orderpoint_product_min_qty')
    def _check_orderpoint_product_qty(self):
        for orderpoint in self:
            if orderpoint.orderpoint_product_max_qty < 0 \
                    or orderpoint.orderpoint_product_min_qty < 0:
                raise exceptions.Warning(
                    _('Orderpoint product quantity cannot be negative'))
