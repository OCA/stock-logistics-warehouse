# Copyright (c) 2019 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockRequest(models.Model):
    _inherit = "stock.request"

    direction = fields.Selection(
        [("outbound", "Outbound"), ("inbound", "Inbound")],
        states={"draft": [("readonly", False)]},
        readonly=True,
    )

    @api.onchange("direction")
    def _onchange_location_id(self):
        if not self._context.get("default_location_id"):
            if self.direction == "outbound":
                # Stock Location set to Partner Locations/Customers
                self.location_id = self.company_id.partner_id.property_stock_customer.id
            else:
                # Otherwise the Stock Location of the Warehouse
                self.location_id = self.warehouse_id.lot_stock_id.id
