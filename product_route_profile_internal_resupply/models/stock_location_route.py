# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"

    internal_supply = fields.Boolean(
        string="Internal Supply",
        readonly=True,
    )
