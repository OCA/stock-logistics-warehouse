# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        values = super()._prepare_procurement_values(group_id)
        values['date_priority'] = self.create_date
        return values
