# -*- coding: utf-8 -*-
# Copyright 2018 PlanetaTIC - Francisco Fernández <ffernandez@planetatic.com>
# Copyright 2018 PlanetaTIC - Lluís Rovira <lrovira@planetatic.com>
# Copyright 2020 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    route_mto = fields.Boolean(
        string='Create Procurement',
        readonly=True,
        states={'draft': [('readonly', False)]},
        compute='_get_route_mto',
        inverse='_set_route_mto',
    )

    @api.multi
    def _get_route_mto(self):
        mto_route = self.env['product.template']._get_mto_route()

        for line in self:
            if mto_route:
                line.route_mto = line.route_id.id == mto_route.id\
                    or mto_route in line.product_id.route_ids
            else:
                line.route_mto = False

    @api.multi
    def _set_route_mto(self):
        mto_route = self.env['product.template']._get_mto_route()

        for line in self:
            route_id = False
            if line.route_mto and line.product_id and mto_route:
                route_id = mto_route
            line.route_id = route_id
