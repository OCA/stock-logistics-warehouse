# Copyright 2019 Open Source Integrators
# Copyright 2019-2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    def action_submit(self):
        if not self.stock_request_ids:
            raise UserError(
                _("There should be at least one request item for submiting the order.")
            )
        for line in self.stock_request_ids:
            line.action_submit()
        self.state = "submitted"
        return True
