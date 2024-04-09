# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    use_purchase_uom = fields.Boolean(
        help="Use the product purchase UoM instead of the default UoM "
        "for the moves belonging to this operation type"
    )
