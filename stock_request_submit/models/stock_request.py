# Copyright 2019 Open Source Integrators
# Copyright 2019-2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockRequest(models.Model):
    _inherit = "stock.request"

    state = fields.Selection(selection_add=[("submitted", "Submitted"), ("open",)])

    route_id = fields.Many2one(
        states={"draft": [("readonly", False)], "submitted": [("readonly", False)]}
    )

    def action_submit(self):
        self._action_submit()

    def _action_submit(self):
        self.state = "submitted"

    def _skip_procurement(self):
        return (
            super()._skip_procurement()
            and self.state != "submitted"
            or self.product_id.type not in ("consu", "product")
        )
