# Copyright (C) 2022 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    template_id = fields.Many2one("stock.location.content.template", string="Template")
