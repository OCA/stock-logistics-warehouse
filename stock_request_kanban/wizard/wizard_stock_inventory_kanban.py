# Copyright 2017 Creu Blanca
# Copyright 2017-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models


class WizardStockInventoryKanban(models.TransientModel):
    _name = "wizard.stock.inventory.kanban"
    _description = "Stock Inventory Kanban Wizard"
    _inherit = "wizard.stock.request.kanban.abstract"

    inventory_kanban_id = fields.Many2one("stock.inventory.kanban", readonly=True)

    def barcode_ending(self):
        res = super().barcode_ending()
        self.inventory_kanban_id.write({"scanned_kanban_ids": [(4, self.kanban_id.id)]})
        return res

    def validate_kanban(self, barcode):
        res = super().validate_kanban(barcode)
        if not self.inventory_kanban_id.kanban_ids.filtered(
            lambda r: r == self.kanban_id
        ):
            self.status = _("Barcode %s is not in the inventory") % barcode
            self.status_state = 1
            return False
        if self.inventory_kanban_id.scanned_kanban_ids.filtered(
            lambda r: r == self.kanban_id
        ):
            self.status = _("Barcode %s is already scanned") % barcode
            self.status_state = 1
            return False
        return res
