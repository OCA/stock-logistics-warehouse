# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockScrap(models.Model):

    _inherit = 'stock.scrap'

    def _get_preferred_domain(self):
        res = super(StockScrap, self)._get_preferred_domain()
        if not self.picking_id:
            res.extend([[('reservation_id', '=', False)]])
        return res
