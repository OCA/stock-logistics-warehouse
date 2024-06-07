# Copyright 2017-24 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = "stock.quant"

    removal_priority = fields.Integer(
        related="location_id.removal_priority", store=True
    )

    @api.model
    def _get_removal_strategy_domain_order(self, domain, removal_strategy, qty):
        if self.user_has_groups(
            "stock_removal_location_by_priority.group_removal_priority"
        ):
            if removal_strategy == "fifo":
                return domain, "in_date ASC, removal_priority ASC, id"
            elif removal_strategy == "lifo":
                return domain, "in_date DESC, removal_priority ASC, id desc"
            raise UserError(
                _("Removal strategy %s not implemented.") % (removal_strategy,)
            )
        return super()._get_removal_strategy_domain_order(domain, removal_strategy, qty)

    def _get_removal_strategy_sort_key(self, removal_strategy):
        key, reverse = super()._get_removal_strategy_sort_key(removal_strategy)
        if removal_strategy == "fifo":
            key = lambda q: (q.removal_priority, q.in_date, q.id)  # noqa: E731
        return key, reverse
