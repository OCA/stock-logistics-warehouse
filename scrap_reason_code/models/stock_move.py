# Copyright (C) 2019 IBM Corp.
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    reason_code_id = fields.Many2one("scrap.reason.code", string="Reason code")
