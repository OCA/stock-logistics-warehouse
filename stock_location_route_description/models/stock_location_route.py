# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"

    description = fields.Char(translate=True)

    def name_get(self):
        if self.env.context.get("show_description", False):
            result = []
            for rec in self:
                name = ""
                if rec.description:
                    name = rec.name + ": " + rec.description
                else:
                    name = rec.name
                result.append((rec.id, name))
            return result
        return super().name_get()
