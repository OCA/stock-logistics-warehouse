# -*- coding: utf-8 -*-
# Copyright 2018 PlanetaTIC - Francisco Fernández <ffernandez@planetatic.com>
# Copyright 2018 PlanetaTIC - Lluís Rovira <lrovira@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_mto_route(self):
        mto_route_id = self.env['ir.model.data'].xmlid_to_res_id(
            'stock.route_warehouse0_mto')
        if mto_route_id:
            return [mto_route_id]
        return []
