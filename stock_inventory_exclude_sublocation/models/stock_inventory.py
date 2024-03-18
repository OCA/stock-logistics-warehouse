# Copyright 2019 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Inventory(models.Model):
    _inherit = "stock.inventory"

    exclude_sublocation = fields.Boolean(
        string="Exclude Sublocations",
        default=False,
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    def _get_base_domain(self, locations):
        res = super()._get_base_domain(locations=locations)
        if not self.exclude_sublocation:
            return res
        return [("location_id", "in", locations.mapped("id"))]
