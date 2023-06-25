# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class StockLocationLock(models.TransientModel):
    _name = "stock.location.lock"
    _description = "Stock Transfer Lock Date"

    location_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Locations",
        domain=[("usage", "=", "internal")],
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
        # raise UserError(self.location_ids)
        self._reset_physical_count_lockdown()
        for rec in self.location_ids:
            rec.sudo().write({"is_physical_count_lockdown": True})
