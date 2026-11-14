# Copyright 2026 Camptocamp SA
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    unpack_at_reception = fields.Boolean(
        help="Packages arriving in this location are unpacked when the transfer "
        "is validated: their content stays in this location, without a package.",
    )
