# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_quant_no_inventory_if_being_picked = fields.Boolean(
        string="Stock quant no inventory if being picked",
        help="If checked, the system will prevent inventory of stock quants if "
        "some quantities are currently being picked for the same product, "
        "location, lot and package.",
        default=False,
    )
