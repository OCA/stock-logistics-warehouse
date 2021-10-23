# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    origin_country_id = fields.Many2one(
        comodel_name="res.country",
        string="Country of Origin",
        help="Country of origin of the product i.e. product " "'made in ____'.",
        index=True,
    )
