# Copyright 2016-2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _onchange_product_id_check_availability(self):
        return super(SaleOrderLine,
                     self.sudo())._onchange_product_id_check_availability()
