# Copyright 2017-2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _get_rule(self, product_id, location_id, values):
        result = super()._get_rule(product_id, location_id, values)
        # If there isn't a date planned in the values it means that this
        # method has been called outside of a procurement process.
        if (
            result
            and not values.get("group_id")
            and result.auto_create_group
            and values.get("date_planned")
        ):
            group_data = self._prepare_auto_procurement_group_data()
            group = self.env["procurement.group"].create(group_data)
            values["group_id"] = group
        return result

    @api.model
    def _prepare_auto_procurement_group_data(self):
        name = self.env["ir.sequence"].next_by_code("procurement.group") or False
        if not name:
            raise UserError(_("No sequence defined for procurement group."))
        return {
            "name": name,
        }
