#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

from odoo import models


class ProductHistory(models.Model):
    _inherit = "product.history"

    # Private section
    def _update_cpol(self):
        context = self.env.context
        model = context.get("active_model")
        if model == "computed.purchase.order.line":
            active_ids = context.get("active_ids")
            cpols = self.env[model].browse(active_ids)
            lines = cpols.exists()
            for line in lines:
                line.displayed_average_consumption = (
                    line.product_id.displayed_average_consumption
                )
            return lines.view_history()
        return False

    def ignore_line(self):
        res = super().ignore_line()
        update_res = self._update_cpol()
        if update_res:
            return update_res
        return res

    def unignore_line(self):
        res = super().unignore_line()
        update_res = self._update_cpol()
        if update_res:
            return update_res
        return res
