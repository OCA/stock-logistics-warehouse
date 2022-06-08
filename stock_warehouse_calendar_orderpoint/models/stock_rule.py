# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import _, models
from odoo.tools import misc


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_lead_days(self, product):
        delay, delay_description = super()._get_lead_days(product)
        if self.env.context.get("orderpoint_id"):
            op_id = self.env.context["orderpoint_id"]
            op = self.env["stock.warehouse.orderpoint"].browse(op_id)
            reordering_date = op._get_next_reordering_date()
            # Display the reordering date first so the user will know from which
            # date the computation is done.
            if reordering_date:
                reordering_date = misc.format_date(self.env, reordering_date)
                title = _("Reordering Date")
                delay_description = (
                    f"<tr><td>{title}</td><td class='text-right'>{reordering_date}</td></tr>"
                    + delay_description
                )
        return delay, delay_description
