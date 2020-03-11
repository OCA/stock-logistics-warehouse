# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, fields, models


class StockMoveCheckoutSync(models.TransientModel):
    _name = "stock.move.checkout.sync"
    _description = "Stock Move Checkout Sync"

    picking_ids = fields.Many2many(comodel_name="stock.picking", required=True)
    dest_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        required=True,
        readonly=True,
        help="Destination operation for these moves.",
    )
    # in case we have several steps to sync all the moves,
    # this field will contain them
    remaining_help = fields.Html(readonly=True)
    done_dest_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        relation="stock_move_checkout_sync_stock_picking_done_dest_rel",
    )
    show_skip_button = fields.Boolean(default=False)
    picking_type_location_id = fields.Many2one(
        related="dest_picking_id.picking_type_id.default_location_src_id",
        readonly=True,
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        help="Destination location where all the moves will be sent.",
    )
    move_ids = fields.Many2many(comodel_name="stock.move", readonly=True)

    def _create_self(self, pickings, done_dest_pickings=None):
        if not done_dest_pickings:
            done_dest_pickings = self.env["stock.picking"].browse()
        values = self._prepare_values_checkout_sync_wizard(
            pickings, done_dest_pickings=done_dest_pickings
        )
        if values:
            return self.create(values)
        return self.browse()

    def _open(self, pickings, done_dest_pickings=None):
        wizard = self._create_self(pickings, done_dest_pickings=done_dest_pickings)
        if wizard:
            view = self.env.ref("stock_checkout_sync.view_stock_move_checkout_sync")
            return {
                "name": _("Checkout Sync"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": self._name,
                "views": [(view.id, "form")],
                "view_id": view.id,
                "target": "new",
                "res_id": wizard.id,
                "context": self.env.context,
            }

    def _remaining_html_fragment(self, picking, moves, selected=False):
        if selected:
            return _("<li><strong>{}: {} move(s)</strong></li>").format(
                picking.name, len(moves)
            )
        return _("<li>{}: {} move(s)</li>").format(picking.name, len(moves))

    def _prepare_values_checkout_sync_wizard(self, pickings, done_dest_pickings=None):
        dest_pickings = pickings.mapped("move_lines")._moves_to_sync_checkout()
        html_fragments = []
        dest_picking_to_sync = None
        moves_to_sync = None
        show_skip_button = False
        for picking, moves in dest_pickings.items():
            if picking in done_dest_pickings:
                html_fragments.append(self._remaining_html_fragment(picking, moves))
                continue

            if not dest_picking_to_sync:
                dest_picking_to_sync = picking
                moves_to_sync = moves
                html_fragments.append(
                    self._remaining_html_fragment(picking, moves, selected=True)
                )
                continue

            # remaining picking types
            # show the button only if we have a next item in queue
            show_skip_button = True
            html_fragments.append(self._remaining_html_fragment(picking, moves))

        if not moves_to_sync:
            return {}
        current_destination = moves_to_sync.mapped(
            "move_line_ids.location_dest_id"
        ) | moves_to_sync.mapped("location_dest_id")

        values = {
            "picking_ids": pickings.ids,
            "dest_picking_id": dest_picking_to_sync.id,
            "done_dest_picking_ids": [(6, 0, done_dest_pickings.ids)],
            "move_ids": [(6, 0, moves_to_sync.ids)],
            "show_skip_button": show_skip_button,
        }
        if len(html_fragments) > 1:
            # do not show the steps if we have only one
            values["remaining_help"] = "<ul>{}</ul>".format("\n".join(html_fragments))
        if len(current_destination) == 1:
            values["location_id"] = current_destination.id
        return values

    def sync(self):
        self.move_ids.sync_checkout_destination(self.location_id)
        # in case we have to chose the destination for another destination
        # picking type with the sync activated, reopen the wizard to update the
        # next round of moves (the wizard will be reopened as many times as we
        # have different destination checkout picking types)
        done_dest_pickings = self.done_dest_picking_ids | self.dest_picking_id
        return self._open(self.picking_ids, done_dest_pickings=done_dest_pickings)

    def skip_to_next(self):
        done_dest_pickings = self.done_dest_picking_ids | self.dest_picking_id
        return self._open(self.picking_ids, done_dest_pickings=done_dest_pickings)
