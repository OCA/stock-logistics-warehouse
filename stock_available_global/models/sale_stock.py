# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _onchange_product_id_check_availability(self):
        return super(SaleOrderLine,
                     self.sudo())._onchange_product_id_check_availability()
