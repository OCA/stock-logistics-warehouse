# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockScrap(models.Model):

    _inherit = "stock.scrap"

    in_progress_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        compute="_compute_in_progress_picking_ids",
        help="This indicates that an operation is in progress for the product and "
        "the source location.",
    )

    @api.model
    def _scrap_origin_common_keys(self):
        """Return the list of fields that are used to select scrap from move lines."""
        return [
            "location_id",
            "product_id",
            "lot_id",
            "package_id",
            "owner_id",
            "company_id",
        ]

    @api.depends("product_id", "location_id")
    def _compute_in_progress_picking_ids(self):
        """
        Compute the pickings that are in progress
        for the origin locations of the scraps.
        """
        move_lines = self.env["stock.move.line"].search(
            [
                ("state", "not in", ("done", "cancel")),
                ("product_id", "in", self.product_id.ids),
                ("location_id", "in", self.mapped("location_id").ids),
                ("qty_done", ">", 0.0),
            ]
        )
        for _key, scrap in self.partition(
            lambda a_scrap: dict(
                {key: a_scrap[key] for key in self._scrap_origin_common_keys()}
            )
        ).items():
            scrap.in_progress_picking_ids = move_lines.filtered(
                lambda line: all(
                    (line[move_key] == scrap.mapped(move_key))
                    for move_key in self._scrap_origin_common_keys()
                )
            ).picking_id

    def do_scrap(self):
        """
        Check that no pickings are in progress before validating the scrap
        """
        for scrap in self:
            if scrap.in_progress_picking_ids:
                picking_names = " ".join(scrap.in_progress_picking_ids.mapped("name"))
                raise UserError(
                    _(
                        "Some picking operations are in progress. You cannot do a scrap "
                        "at the same time. \n\nPickings concerned: %(picking_names)s",
                        picking_names=picking_names,
                    )
                )
        return super().do_scrap()
