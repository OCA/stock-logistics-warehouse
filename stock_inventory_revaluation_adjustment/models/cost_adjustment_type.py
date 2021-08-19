# Copyright 2021 - Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CostAdjustmentType(models.Model):
    _name = "cost.adjustment.type"
    _description = "Cost Adjustment Type"
    _order = "name"

    name = fields.Char(string="Name", required=True)
    account_id = fields.Many2one("account.account", string="Account")
    active = fields.Boolean(default=True)
