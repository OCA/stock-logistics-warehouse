# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_confirm(self):
        for picking in self:
            if (
                picking.picking_type_id.auto_procurement_group
                and not picking.move_ids.group_id
                and not picking.move_ids.rule_id
            ):
                group = self.env["procurement.group"].create(
                    {
                        "move_type": picking.move_type,
                        "partner_id": picking.partner_id,
                    }
                )
                picking.move_ids.write({"group_id": group.id})
        return super().action_confirm()
