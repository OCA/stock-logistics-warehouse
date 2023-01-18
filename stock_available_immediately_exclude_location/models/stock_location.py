# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):

    _inherit = "stock.location"

    exclude_from_immediately_usable_qty = fields.Boolean(
        "Exclude from immediately usable quantity",
        default=False,
        index=True,
        help="This property is not inherited by children locations",
    )
