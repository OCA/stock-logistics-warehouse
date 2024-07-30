# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import config


class StockLocation(models.Model):
    _inherit = "stock.location"

    def _skip_check_archive_constraint_condition(self):
        return config["test_enable"] and not self.env.context.get(
            "test_stock_archive_constraint"
        )

    @api.constrains("active")
    def _check_active_stock_archive_constraint_stock_quant(self):
        if self._skip_check_archive_constraint_condition():
            return
        res = self.env["stock.quant"].search(
            [
                "&",
                ("location_id.usage", "in", ("internal", "transit")),
                "|",
                ("location_id", "in", self.filtered(lambda x: not x.active).ids),
                ("location_id", "child_of", self.filtered(lambda x: not x.active).ids),
            ],
            limit=1,
        )
        if res:
            raise ValidationError(
                _(
                    "It is not possible to archive location "
                    "'%(display_name)s' which has "
                    "associated stock quantities."
                )
                % {"display_name": res.display_name}
            )

    @api.constrains("active")
    def _check_active_stock_archive_constraint_stock_move(self):
        if self._skip_check_archive_constraint_condition():
            return
        res = self.env["stock.move"].search(
            [
                "&",
                ("state", "not in", ("done", "cancel")),
                "|",
                ("location_id", "in", self.filtered(lambda x: not x.active).ids),
                ("location_id", "child_of", self.filtered(lambda x: not x.active).ids),
            ],
            limit=1,
        )
        if res:
            raise ValidationError(
                _(
                    "It is not possible to archive location "
                    "'%(display_name)s' which has "
                    "associated picking lines."
                )
                % {"display_name": res.display_name}
            )

    @api.constrains("active")
    def _check_active_stock_archive_constraint_stock_move_line(self):
        if self._skip_check_archive_constraint_condition():
            return
        res = self.env["stock.move.line"].search(
            [
                "&",
                ("state", "not in", ("done", "cancel")),
                "|",
                ("location_id", "in", self.filtered(lambda x: not x.active).ids),
                ("location_id", "child_of", self.filtered(lambda x: not x.active).ids),
            ],
            limit=1,
        )
        if res:
            raise ValidationError(
                _(
                    "It is not possible to archive location "
                    "'%(display_name)s' which has "
                    "associated stock reservations."
                )
                % {"display_name": res.display_name}
            )
