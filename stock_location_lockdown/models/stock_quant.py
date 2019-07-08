# -*- coding: utf-8 -*-
# Copyright 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.constrains('location_id')
    def _check_location_blocked(self):
        for record in self:
            if record.location_id.block_stock_entrance:
                raise ValidationError(
                    _('The location %s is blocked and can '
                      'not be used for moving the product %s')
                    % (record.location_id.name, record.product_id.name)
                    )
        return True
