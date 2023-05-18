# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    orig_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        relation="stock_picking_orig_dest_rel",
        column1="dest_picking_id",
        column2="orig_picking_id",
        string="Origin Transfer/s",
        compute="_compute_origin_dest_picking",
        store=True,
        readonly=True,
    )
    dest_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        relation="stock_picking_orig_dest_rel",
        column1="orig_picking_id",
        column2="dest_picking_id",
        string="Destination Transfer/s",
        compute="_compute_origin_dest_picking",
        store=True,
        readonly=True,
    )

    def _get_orig_picking_ids(self):
        """
        Returns the Origin Pickings from a single picking. Done in method to be
        inherited in other modules, if needed.
        """
        self.ensure_one()
        return self.mapped("move_lines.move_orig_ids.picking_id")

    def _get_dest_picking_ids(self):
        """
        Returns the Destination Pickings from a single picking. Done in method to be
        inherited in other modules, if needed.
        """
        self.ensure_one()
        return self.mapped("move_lines.move_dest_ids.picking_id")

    @api.depends("move_lines.move_orig_ids", "move_lines.move_dest_ids")
    def _compute_origin_dest_picking(self):
        for picking in self:
            picking.orig_picking_ids = picking._get_orig_picking_ids()
            picking.dest_picking_ids = picking._get_dest_picking_ids()
