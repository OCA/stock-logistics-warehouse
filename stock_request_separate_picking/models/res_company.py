# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_request_allow_separate_picking = fields.Boolean(
        string="Allow Separate Picking on Stock Requests"
    )
