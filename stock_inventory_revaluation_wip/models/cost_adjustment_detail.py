# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CostAdjustmentDetail(models.Model):
    _inherit = "stock.cost.adjustment.detail"

    operation_id = fields.Many2one(
        "mrp.routing.workcenter",
        string="Operations",
    )
