# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockInventory(models.Model):
    _name = "stock.inventory"
    _inherit = ["stock.inventory", "tier.validation"]
    _state_from = ["draft", "confirm"]
    _state_to = ["done"]

    _tier_validation_manual_config = False
