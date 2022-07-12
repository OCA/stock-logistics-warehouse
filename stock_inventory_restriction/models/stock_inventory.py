# Copyright 2022 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Inventory(models.Model):
    _inherit = "stock.inventory"

    user_id = fields.Many2one(comodel_name="res.users", string="User")
