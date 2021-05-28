# Copyright 2020 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class VerticalLiftOperationTransfer(models.AbstractModel):
    _inherit = "vertical.lift.operation.transfer"

    product_qty_by_packaging_display = fields.Char(
        compute="_compute_product_qty_by_packaging_display"
    )

    @api.depends("current_move_line_id.product_qty")
    def _compute_product_qty_by_packaging_display(self):
        # Seems the ctx key is not propagated on a related field
        # nor from the field definition, nor from the field declaration in the view.
        # Hence, we are forced to use a computed field.
        for rec in self.with_context(qty_by_pkg_total_units=True):
            rec.product_qty_by_packaging_display = (
                rec.current_move_line_id.product_qty_by_packaging_display
            )
