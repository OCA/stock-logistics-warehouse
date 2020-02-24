# Copyright 2020 PESOL - Angel Moya
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    quant_manual_assign_update_qty_done = fields.Boolean(
        string='Update Qty Done On Quant Manual Assign',
        default=True)
