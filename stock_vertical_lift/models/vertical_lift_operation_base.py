# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import namedtuple

from odoo import _, api, fields, models

from odoo.addons.base_sparse_field.models.fields import Serialized

_logger = logging.getLogger(__name__)


# The following methods have been copied from 'shopfloor' module (OCA/wms)
# https://github.com/OCA/wms/blob/14.0/shopfloor/models/stock_move.py#L19
# TODO: we should move them in a generic module


def split_other_move_lines(move, move_lines):
    """Substract `move_lines` from `move.move_line_ids`, put the result
    in a new move and returns it.
    """
    other_move_lines = move.move_line_ids - move_lines
    if other_move_lines or move.state == "partially_available":
        qty_to_split = move.product_uom_qty - sum(move_lines.mapped("product_uom_qty"))
        backorder_move_vals = move._split(qty_to_split)
        backorder_move = move.create(backorder_move_vals)
        if not backorder_move:
            return False
        backorder_move._action_confirm(merge=False)
        backorder_move.move_line_ids = other_move_lines
        backorder_move._recompute_state()
        backorder_move._action_assign()
        move._recompute_state()
        return backorder_move
    return False


def extract_and_action_done(move):
    """Extract the moves in a separate transfer and validate them.

    You can combine this method with `split_other_move_lines` method
    to first extract some move lines in a separate move, then validate it
    with this method.
    """
    # Put remaining qty to process from partially available moves
    # in their own move (which will be then 'confirmed')
    partial_moves = move.filtered(lambda m: m.state == "partially_available")
    for partial_move in partial_moves:
        split_other_move_lines(partial_move, partial_move.move_line_ids)
    # Process assigned moves
    moves = move.filtered(lambda m: m.state == "assigned")
    if not moves:
        return False
    for picking in moves.picking_id:
        moves_todo = picking.move_lines & moves
        if moves_todo == picking.move_lines:
            # No need to create a new transfer if we are processing all moves
            new_picking = picking
        else:
            new_picking = picking.copy(
                {
                    "name": "/",
                    "move_lines": [],
                    "move_line_ids": [],
                    "backorder_id": picking.id,
                }
            )
            new_picking.message_post(
                body=_(
                    "Created from backorder "
                    "<a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a>."
                )
                % (picking.id, picking.name)
            )
            moves_todo.write({"picking_id": new_picking.id})
            moves_todo.package_level_id.write({"picking_id": new_picking.id})
            moves_todo.move_line_ids.write({"picking_id": new_picking.id})
            moves_todo.move_line_ids.package_level_id.write(
                {"picking_id": new_picking.id}
            )
            new_picking.action_assign()
            assert new_picking.state == "assigned"
        new_picking._action_done()
    return True


# /methods


class VerticalLiftOperationBase(models.AbstractModel):
    """Base model for shuttle operations (pick, put, inventory)"""

    _name = "vertical.lift.operation.base"
    _inherit = "barcodes.barcode_events_mixin"
    _description = "Vertical Lift Operation - Base"

    name = fields.Char(related="shuttle_id.name", readonly=True)
    shuttle_id = fields.Many2one(
        comodel_name="vertical.lift.shuttle", required=True, readonly=True
    )
    location_id = fields.Many2one(related="shuttle_id.location_id", readonly=True)
    number_of_ops = fields.Integer(
        compute="_compute_number_of_ops", string="Number of Operations"
    )
    number_of_ops_all = fields.Integer(
        compute="_compute_number_of_ops_all",
        string="Number of Operations in all shuttles",
    )
    mode = fields.Selection(related="shuttle_id.mode", readonly=True)

    state = fields.Selection(
        selection=lambda self: self._selection_states(),
        default=lambda self: self._initial_state,
    )
    _initial_state = None  # to define in sub-classes

    # if there is an action and it's returning True, the transition is done,
    # otherwise not
    Transition = namedtuple("Transition", "current_state next_state action direct_eval")
    # default values to None
    Transition.__new__.__defaults__ = (None,) * len(Transition._fields)

    _sql_constraints = [
        (
            "shuttle_id_unique",
            "UNIQUE(shuttle_id)",
            "One pick can be run at a time for a shuttle.",
        )
    ]

    def _selection_states(self):
        return []

    def _transitions(self):
        """Define the transitions between the states

        To set in sub-classes.
        It is a tuple of a ``Transition`` instances, evaluated in order.
        A transition has a source step, a destination step, a function and a
        flag ``direct_eval``.
        When the function returns True, the transition is applied, otherwise,
        the next transition matching the current step is evaluated.
        When a transition has no function, it is always applied.
        The flag ``direct_eval`` indicates that the workflow should directly
        evaluates again the transitions to reach the next step. It allows to
        use "virtual" steps that will never be kept for users but be used as
        router.

        The initial state must be defined in the attribute ``_initial_state``.

        The transition from a step to another are triggered by a call to
        ``next_step()``. This method is called in several places:

        * ``reset_steps()`` (called when the screen opens)
        * ``button_save()``, generally used to post the move
        * ``button_release()``, generally used to go to the next line
        * ``on_barcode_scanned()``, the calls to ``next_step()`` are to
          implement in sub-classed if the scanned barcode leads to the next
          step

        Example of workflow described below:

        ::
            _initial_state = "noop"

            def _selection_states(self):
                return [
                    ("noop", "No operations"),
                    ("scan_destination", "Scan New Destination Location"),
                    ("save", "Put goods in tray and save"),
                    ("release", "Release"),
                ]

            def _transitions(self):
                return (
                    self.Transition(
                        "noop",
                        "scan_destination",
                        lambda self: self.select_next_move_line()
                    ),
                    self.Transition("scan_destination", "save"),
                    self.Transition("save", "release"),
                    self.Transition(
                        "release",
                        "scan_destination",
                        lambda self: self.select_next_move_line()
                    ),
                    self.Transition("release", "noop"),
                )

        When we arrive on the screen, the ``on_screen_open`` methods resets the
        steps (``reset_steps()``). It ensures the current step is ``noop`` and
        directly tries to reach the next step (call to ``next_step()``).

        It tries to go from ``noop`` to ``scan_destination``, calling
        ``self.select_next_move_line()``. If the method finds a line, it
        returns True and the transition is applied, otherwise, the step stays
        ``noop``.

        The transitions from ``scan_destination`` and ``save`` and from
        ``save`` and ``release`` are always applied when ``next_step()`` is
        called (``scan_destination`` → ``save`` from ``on_barcode_scanned``
        when a destination was found, ``save`` → ``release`` from the save
        button).

        When ``button_release()`` is called, it calls ``next_step()`` which
        first evaluates ``self.select_next_move_line()``: if a move line remains, it
        goes to ``scan_destination``, otherwise to ``noop``.

        """
        return ()

    def step(self):
        return self.state

    def next_step(self, direct_eval=False):
        current_state = self.state
        for transition in self._transitions():
            if direct_eval and not transition.direct_eval:
                continue
            if transition.current_state != current_state:
                continue
            if not transition.action or transition.action(self):
                _logger.debug(
                    "Transition %s → %s",
                    transition.current_state,
                    transition.next_state,
                )
                self.state = transition.next_state
                break
        # reevaluate the transitions if we have a new state with direct_eval transitions
        if self.state != current_state and any(
            transition.direct_eval
            for transition in self._transitions()
            if transition.current_state == self.state
        ):
            self.next_step(direct_eval=True)

    def reset_steps(self):
        if not self._initial_state:
            raise NotImplementedError("_initial_state must be defined")
        self.state = self._initial_state
        self.next_step()

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        # to implement in sub-classes

    def on_screen_open(self):
        """Called when the screen is opened"""
        self.reset_steps()

    def onchange(self, values, field_name, field_onchange):
        if field_name == "_barcode_scanned":
            # _barcode_scanner is implemented (in the barcodes module) as an
            # onchange, which is really annoying when we want it to act as a
            # normal button and actually have side effect in the database
            # (update line, go to the next step, ...). This override shorts the
            # onchange call and calls the scanner method as a normal method.
            self.on_barcode_scanned(values["_barcode_scanned"])
            # We can't know which fields on_barcode_scanned changed, refresh
            # everything.
            return {"value": self.read()[0]}
        else:
            return super().onchange(values, field_name, field_onchange)

    @api.depends()
    def _compute_number_of_ops(self):
        for record in self:
            record.number_of_ops = 0

    @api.depends()
    def _compute_number_of_ops_all(self):
        for record in self:
            record.number_of_ops_all = 0

    def action_open_screen(self):
        return self.shuttle_id.action_open_screen()

    def action_menu(self):
        return self.shuttle_id.action_menu()

    def action_manual_barcode(self):
        return self.shuttle_id.action_manual_barcode()

    def process_current(self):
        """Process the action (pick, put, ...)

        To implement in sub-classes
        """
        raise NotImplementedError

    def button_save(self):
        """Confirm the operation (set move to done, ...)"""
        self.ensure_one()
        if not self.step() == "save":
            return
        self.next_step()

    def button_release(self):
        """Release the operation, go to the next"""
        self.ensure_one()
        if not self.step() == "release":
            return
        return self.next_step()

    def _render_product_packagings(self, product):
        if not product:
            return ""
        return self.env["ir.qweb"]._render(
            "stock_vertical_lift.packagings",
            self._prepare_values_for_product_packaging(product),
        )

    def _prepare_values_for_product_packaging(self, product):
        return {"product": product}

    def _get_tray_qty(self, product, location):
        quants = self.env["stock.quant"].search(
            [("location_id", "=", location.id), ("product_id", "=", product.id)]
        )
        return sum(quants.mapped("quantity"))

    def _rainbow_man(self, message=None):
        if not message:
            message = _("Congrats, you cleared the queue!")
        return {
            "effect": {
                "fadeout": "slow",
                "message": message,
                "img_url": "/web/static/src/img/smile.svg",
                "type": "rainbow_man",
            }
        }

    def _send_notification_refresh(self):
        """Send a refresh notification

        Generally, you want to call the method
        _send_notification_refresh() on VerticalLiftShuttle so you
        don't need to know the id of the current operation.

        Other notifications can be implemented, they have to be
        added in static/src/js/vertical_lift.js and the message
        must contain an "action" and "params".
        """
        self.ensure_one()
        channel = "notify_vertical_lift_screen"
        bus_message = {
            "action": "refresh",
            "params": {"model": self._name, "id": self.id},
        }
        self.env["bus.bus"].sendone(channel, bus_message)


class VerticalLiftOperationTransfer(models.AbstractModel):
    """Base model for shuttle pick and put operations"""

    _name = "vertical.lift.operation.transfer"
    _inherit = "vertical.lift.operation.base"
    _description = "Vertical Lift Operation - Transfer"

    current_move_line_id = fields.Many2one(
        comodel_name="stock.move.line", readonly=True
    )

    tray_location_id = fields.Many2one(
        comodel_name="stock.location",
        compute="_compute_tray_data",
        string="Tray Location",
    )
    tray_name = fields.Char(compute="_compute_tray_data", string="Tray Name")
    tray_type_id = fields.Many2one(
        comodel_name="stock.location.tray.type",
        compute="_compute_tray_data",
        string="Tray Type",
    )
    tray_type_code = fields.Char(compute="_compute_tray_data", string="Tray Code")
    tray_x = fields.Integer(string="X", compute="_compute_tray_data")
    tray_y = fields.Integer(string="Y", compute="_compute_tray_data")
    tray_matrix = Serialized(string="Cells", compute="_compute_tray_data")
    tray_qty = fields.Float(string="Stock Quantity", compute="_compute_tray_qty")

    # current operation information
    picking_id = fields.Many2one(
        related="current_move_line_id.picking_id", readonly=True
    )
    picking_origin = fields.Char(
        related="current_move_line_id.picking_id.origin", readonly=True
    )
    picking_partner_id = fields.Many2one(
        related="current_move_line_id.picking_id.partner_id", readonly=True
    )
    product_id = fields.Many2one(
        related="current_move_line_id.product_id", readonly=True
    )
    product_uom_id = fields.Many2one(
        related="current_move_line_id.product_uom_id", readonly=True
    )
    product_uom_qty = fields.Float(
        related="current_move_line_id.product_uom_qty", readonly=True
    )
    product_packagings = fields.Html(
        string="Packaging", compute="_compute_product_packagings"
    )
    qty_done = fields.Float(related="current_move_line_id.qty_done", readonly=True)
    lot_id = fields.Many2one(related="current_move_line_id.lot_id", readonly=True)
    location_dest_id = fields.Many2one(
        string="Destination",
        related="current_move_line_id.location_dest_id",
        readonly=False,
    )
    # TODO add a glue addon with product_expiry to add the field

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        self.env.user.notify_info(
            "Scanned barcode: {}. Not implemented.".format(barcode)
        )

    @api.depends("current_move_line_id.product_id.packaging_ids")
    def _compute_product_packagings(self):
        for record in self:
            product = record.current_move_line_id.product_id
            # Empty product is taken care in _render_product_packagings
            content = self._render_product_packagings(product)
            record.product_packagings = content

    @api.depends()
    def _compute_number_of_ops(self):
        for record in self:
            record.number_of_ops = record.count_move_lines_to_do()

    @api.depends()
    def _compute_number_of_ops_all(self):
        for record in self:
            record.number_of_ops_all = record.count_move_lines_to_do_all()

    @api.depends("tray_location_id", "current_move_line_id.product_id")
    def _compute_tray_qty(self):
        for record in self:
            if not (record.tray_location_id and record.current_move_line_id):
                record.tray_qty = 0.0
                continue
            product = record.current_move_line_id.product_id
            location = record.tray_location_id
            record.tray_qty = self._get_tray_qty(product, location)

    @api.depends("current_move_line_id")
    def _compute_tray_data(self):
        for record in self:
            modes = {"pick": "location_id", "put": "location_dest_id"}
            location = record.current_move_line_id[modes[record.mode]]
            tray_type = location.location_id.tray_type_id
            # this is the current cell
            record.tray_location_id = location.id
            # name of the tray where the cell is
            record.tray_name = location.location_id.name
            record.tray_type_id = tray_type.id
            record.tray_type_code = tray_type.code
            record.tray_x = location.posx
            record.tray_y = location.posy
            record.tray_matrix = location.tray_matrix

    def _domain_move_lines_to_do(self):
        # to implement in sub-classes
        return [("id", "=", 0)]

    def _domain_move_lines_to_do_all(self):
        # to implement in sub-classes
        return [("id", "=", 0)]

    def count_move_lines_to_do(self):
        """Count move lines to process in current shuttles"""
        self.ensure_one()
        return self.env["stock.move.line"].search_count(self._domain_move_lines_to_do())

    def count_move_lines_to_do_all(self):
        """Count move lines to process in all shuttles"""
        self.ensure_one()
        return self.env["stock.move.line"].search_count(
            self._domain_move_lines_to_do_all()
        )

    def process_current(self):
        line = self.current_move_line_id
        if line.state in ("assigned", "partially_available"):
            line.qty_done = line.product_qty
            # if the move has other move lines, it is split to have only this move line
            split_other_move_lines(line.move_id, line)
            extract_and_action_done(line.move_id)
        return True

    def fetch_tray(self):
        raise NotImplementedError

    def reset_steps(self):
        self.clear_current_move_line()
        super().reset_steps()

    def clear_current_move_line(self):
        self.current_move_line_id = False
        return True
