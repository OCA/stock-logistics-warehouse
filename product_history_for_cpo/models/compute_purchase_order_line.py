#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

from odoo import fields, models


class ComputedPurchaseOrderLine(models.Model):
    _inherit = "computed.purchase.order.line"

    # Columns section
    displayed_product_history_ids = fields.One2many(
        "product.history",
        related="product_id.product_history_ids",
        string="Product History",
    )

    # Private section
    def view_history(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "product_history.action_history_view"
        )
        ids = []
        history_ranges = []
        for cpol in self:
            ids.append(cpol.product_id.id)
            history_ranges.append(cpol.product_id.history_range)
        action["domain"] = [
            ("product_id", "in", ids),
            ("history_range", "in", history_ranges),
        ]
        action["target"] = "new"
        action["context"] = {
            "active_model": "computed.purchase.order.line",
            "active_id": self and self[0].id,
            "active_ids": self.ids,
        }
        return action
