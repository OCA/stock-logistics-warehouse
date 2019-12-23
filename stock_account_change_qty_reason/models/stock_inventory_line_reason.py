# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockAccountInventoryChangeReason(models.Model):
    _inherit = "stock.inventory.line.reason"

    account_reason_input_id = fields.Many2one(
        "account.account",
        string="Input Account for Stock Valuation",
        help="When set, it will be used as offsetting account when "
        "products are received into the company.",
    )
    account_reason_output_id = fields.Many2one(
        "account.account",
        string="Output Account for Stock Valuation",
        help="When set, it will be used as offsetting account when "
        "products are issued from the company.",
    )
