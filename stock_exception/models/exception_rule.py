# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    picking_ids = fields.Many2many(comodel_name="stock.picking", string="Pickings")
    model = fields.Selection(
        selection_add=[
            ("stock.picking", "Stock Picking"),
            ("stock.move", "Stock Move"),
        ],
        ondelete={"stock.picking": "cascade", "stock.move": "cascade"},
    )
    method = fields.Selection(
        selection_add=[
            ("button_validate", "Validation"),
            ("action_confirm", "Confirmation"),
        ],
        readonly=False,
    )
