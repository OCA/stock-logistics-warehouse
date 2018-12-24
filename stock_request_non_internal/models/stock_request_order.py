# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockRequestOrder(models.Model):
    _inherit = 'stock.request.order'

    @api.constrains('location_id', 'company_id')
    def check_order_company(self):
        if not self.location_id.company_id:
            others = self.search([('location_id', '=', self.location_id.id),
                                  ('company_id', '!=', self.company_id.id)])
            if others:
                raise ValidationError(_(
                    'There are requests for the same location but other'
                    ' company'))
