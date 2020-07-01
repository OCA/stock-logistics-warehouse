# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    virtual_location_id = fields.Many2one(
        comodel_name="stock.location", domain=[("usage", "like", "inventory")],
    )

    def _get_virtual_location(self):
        return self.virtual_location_id or super()._get_virtual_location()
