# Copyright 2019 ForgeFlow S.L. (http://www.forgeflow.com)
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Inventory(models.Model):
    _inherit = "stock.inventory"

    exclude_sublocation = fields.Boolean(
        string="Exclude Sublocations",
        default=False,
        track_visibility="onchange",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    def _get_inventory_lines_values(self):
        """Discard inventory lines that are from sublocations if option
        is enabled.

        Done this way for maximizing inheritance compatibility.
        """
        vals = super()._get_inventory_lines_values()
        if not self.exclude_sublocation:
            return vals
        new_vals = []
        for val in vals:
            if val["location_id"] in self.location_ids.ids:
                new_vals.append(val)
        return new_vals
