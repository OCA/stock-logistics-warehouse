# -*- coding: utf-8 -*-
# Copyright 2018 PlanetaTIC - Francisco Fernández <ffernandez@planetatic.com>
# Copyright 2018 PlanetaTIC - Lluís Rovira <lrovira@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _get_route_mto(self):
        mto_route_id = self.env['product.template']._get_mto_route()
        mto_route_id = mto_route_id and mto_route_id[0] or False
        for line in self:
            if mto_route_id and line.id:
                line.route_mto = bool(self.search([
                    ('id', '=', line.id),
                    '|', ('route_id', '=', mto_route_id),
                    ('product_id.route_ids', '=', mto_route_id)
                ]))
            else:
                line.route_mto = False

    @api.multi
    def _set_route_mto(self):
        for line in self:
            route_id = False
            if line.route_mto:
                if line.product_id:
                    mto_route_ids = self.env['product.template'
                                             ]._get_mto_route()
                    if mto_route_ids:
                        route_id = mto_route_ids[0]
            line.route_id = route_id

    route_mto = fields.Boolean(
        string='Create Procurement',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_get_route_mto',
        inverse='_set_route_mto',
    )
