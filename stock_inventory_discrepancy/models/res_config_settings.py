# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    inventory_discrepancy_enable = fields.Boolean(
        string="Inventory Discrepancy Control",
        help="Block validation of the inventory adjustment if discrepancy exceeds "
        "the threshold.",
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env["ir.config_parameter"].sudo()
        inventory_discrepancy_enable = (
            param.get_param(
                "stock_inventory_discrepancy.inventory_discrepancy_enable", default="0"
            )
            == "1"
        )
        res.update(
            inventory_discrepancy_enable=inventory_discrepancy_enable,
        )
        return res

    # pylint: disable=missing-return
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env["ir.config_parameter"].sudo()
        param.set_param(
            "stock_inventory_discrepancy.inventory_discrepancy_enable",
            "1" if self.inventory_discrepancy_enable else "0",
        )
