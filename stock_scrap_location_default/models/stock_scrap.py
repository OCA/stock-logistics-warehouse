# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.stock.models.stock_location import Location as StockLocation


class StockScrap(models.Model):

    _inherit = "stock.scrap"

    def _get_default_scrap_location_id(self) -> StockLocation:
        """
        Returns the default scrap location defined on company level
        """
        if self.env.company.scrap_default_location_id:
            return self.env.company.scrap_default_location_id
        return super()._get_default_scrap_location_id()

    # This is necessary as Odoo still uses (for v<=16) static method for default
    scrap_location_id = fields.Many2one(default=_get_default_scrap_location_id)
