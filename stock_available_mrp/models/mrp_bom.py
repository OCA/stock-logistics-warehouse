# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    add_potential_exception = fields.Boolean(
        string="Avoid adding potential to available to promise",
        help="If potential qty added to available to promise is set in the company "
        "we can override this option for single BoMs",
    )
