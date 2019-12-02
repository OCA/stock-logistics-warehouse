# Copyright 2019 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Preferred Route",
        domain="[('orderpoint_selectable', '=', True)]",
        help="Preferred route for the reordering.",
    )

    def _prepare_procurement_values(
        self, product_qty, date=False, group=False
    ):
        values = super()._prepare_procurement_values(
            product_qty, date=date, group=group
        )
        if self.route_id:
            values = values.copy()
            values["route_ids"] = self.route_id
        return values
