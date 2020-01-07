# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockInventory(models.Model):
    _name = "stock.inventory"
    _inherit = ["stock.inventory", "mail.thread"]

    state = fields.Selection(tracking=True)

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "state" in init_values and self.state == "confirm":
            return self.env.ref("stock_inventory_chatter.mt_inventory_confirmed")
        elif "state" in init_values and self.state == "done":
            return self.env.ref("stock_inventory_chatter.mt_inventory_done")
        return super(StockInventory, self)._track_subtype(init_values)
