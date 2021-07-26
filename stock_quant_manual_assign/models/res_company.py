# Copyright 2021 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_quant_manual_assign_as_done = fields.Boolean(
        string="Manually Assigned Quants Increase Done Quantity",
        default=True,
        help="When using the Manual Quants wizard in operations, a reservation "
        "for the selected quant will be done, you can decide if this will "
        "also automatically increase the done quantity or not",
    )
