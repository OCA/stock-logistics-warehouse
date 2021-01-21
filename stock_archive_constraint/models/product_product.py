# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.constrains("active")
    def _check_active_stock_archive_constraint_stock_quant(self):
        res = self.env["stock.quant"].search(
            [
                ("location_id.usage", "in", ("internal", "transit")),
                ("product_id", "in", self.filtered(lambda x: not x.active).ids),
                ("quantity", "!=", 0.0),
            ],
            limit=1,
        )
        if res:
            raise ValidationError(
                _(
                    "It is not possible to archive product '%s' which has "
                    "associated stock quantities." % res[0].product_id.display_name
                )
            )

    @api.constrains("active")
    def _check_active_stock_archive_constraint_stock_move(self):
        res = self.env["stock.move"].search(
            [
                ("product_id", "in", self.filtered(lambda x: not x.active).ids),
                ("state", "not in", ("done", "cancel")),
            ],
            limit=1,
        )
        if res:
            raise ValidationError(
                _(
                    "It is not possible to archive product '%s' which has "
                    "associated picking lines." % res[0].product_id.display_name
                )
            )

    @api.constrains("active")
    def _check_active_stock_archive_constraint_stock_move_line(self):
        res = self.env["stock.move.line"].search(
            [
                ("product_id", "in", self.filtered(lambda x: not x.active).ids),
                ("state", "not in", ("done", "cancel")),
            ],
            limit=1,
        )
        if res:
            raise ValidationError(
                _(
                    "It is not possible to archive product '%s' which has "
                    "associated stock reservations." % res[0].product_id.display_name
                )
            )
