# Copyright 2021 Sergio Teruel - Tecnativa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    package_grouping = fields.Selection(
        [("standard", "Standard grouping"), ("line", "No line grouping")],
        string="Package grouping",
        default="standard",
        help="Select the behaviour for grouping detailed operations in packages:\n"
        "* Standard grouping (default): All detailed operation will generate "
        "one package always.\n"
        "* No line grouping: Every detailed operation will generate one package."
        "* <empty>: If no value is selected, system-wide default will be used.\n",
    )
