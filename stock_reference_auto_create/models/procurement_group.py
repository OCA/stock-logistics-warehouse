# Copyright 2017-2020 ForgeFlow, S.L.
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _get_rule(self, product_id, location_id, values):
        rule = super()._get_rule(product_id, location_id, values)
        # If there isn't a date planned in the values it means that this
        # method has been called outside of a procurement process.
        if (
            rule
            and not values.get("group_id")
            and rule.auto_create_group
            and values.get("date_planned")
        ):
            values["group_id"] = rule._get_auto_procurement_group(product_id)
        return rule
