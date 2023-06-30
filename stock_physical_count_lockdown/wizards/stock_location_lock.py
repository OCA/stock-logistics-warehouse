# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class StockLocationLock(models.TransientModel):
    _name = "stock.location.lock"
    _description = "Stock Transfer Lock"

    location_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Locations",
        domain=[("usage", "=", "internal")],
    )
    has_clear_all = fields.Boolean(
        string="Clear All Selected",
        help="For clear all selected locations, just click this field and click Update button.",
    )

    @api.model
    def default_get(self, field_list):
        res = super(StockLocationLock, self).default_get(field_list)
        locations = self.location_ids.search(
            [("is_physical_count_lockdown", "=", True)]
        )
        if locations:
            res.update({"location_ids": [(6, 0, [x.id for x in locations])]})
        return res

    def _reset_physical_count_lockdown(self):
        """
        This function will set block stock entrance in all location to False
        """
        locations = self.location_ids.search([("usage", "=", "internal")])
        for rec in locations:
            rec.sudo().write(
                {
                    "is_physical_count_lockdown": False,
                }
            )

    def execute(self):
        self.ensure_one()
        self._reset_physical_count_lockdown()
        if not self.has_clear_all:
            for rec in self.location_ids:
                rec.sudo().write({"is_physical_count_lockdown": True})
