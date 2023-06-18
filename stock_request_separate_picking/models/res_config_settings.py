# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_request_allow_separate_picking = fields.Boolean(
        related="company_id.stock_request_allow_separate_picking",
        readonly=False,
    )
