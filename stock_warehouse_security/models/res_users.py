# Copyright (C) 2019 Akretion
# Copyright 2022 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    warehouse_ids = fields.Many2many(
        "stock.warehouse",
        string="Allowed Warehouses",
    )

    @api.model
    def _get_invalidation_fields(self):
        res = super()._get_invalidation_fields()
        res.add("warehouse_ids")
        return res
