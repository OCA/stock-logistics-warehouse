# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"

    description = fields.Char(translate=True)

    def name_get(self):
        result = []
        if self.env.context.get("show_description", False):
            for rec in self:
                if rec.description:
                    rec.display_name = rec.name + ": " + rec.description
                else:
                    rec.display_name = rec.name
                result.append((rec.id, rec.display_name))
        else:
            for rec in self:
                rec.display_name = rec.name
            return super(StockLocationRoute, self).name_get()
        return result
