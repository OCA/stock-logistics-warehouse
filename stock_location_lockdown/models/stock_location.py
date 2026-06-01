# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = "stock.location"

    block_stock_entrance = fields.Boolean(
        help="If checked, putting stock on this location won't be allowed. "
        "Propagates to descendant locations through the inbound block "
        "aggregation."
    )
    block_stock_exit = fields.Boolean(
        help="If checked, taking stock out of this location won't be allowed. "
        "Quants on this location are treated as if reserved and won't be "
        "available for picking. Propagates to descendant locations through "
        "the outbound block aggregation."
    )
    no_physical_stock = fields.Boolean(
        help="If checked, this location is a grouping / non-physical node: "
        "stock cannot enter or leave it. Use this on internal-tree "
        "intermediate locations that can't be marked as 'View' (Odoo bug "
        "#26679). Does NOT propagate to child locations."
    )
    is_ancestor_inbound_blocked = fields.Boolean(
        compute="_compute_is_ancestor_inbound_blocked",
        store=True,
        recursive=True,
        help="True if a strict ancestor of this location has "
        "'Block Stock Entrance' set.",
    )
    is_ancestor_outbound_blocked = fields.Boolean(
        compute="_compute_is_ancestor_outbound_blocked",
        store=True,
        recursive=True,
        help="True if a strict ancestor of this location has "
        "'Block Stock Exit' set.",
    )
    is_inventory_blocked = fields.Boolean(
        compute="_compute_is_inventory_blocked",
        store=True,
        help="True if the company opts into inventory-driven lockdown and an "
        "in-progress inventory covers this location or any ancestor. "
        "Inventory locks both directions, so a single flag is used.",
    )
    is_inbound_blocked = fields.Boolean(
        compute="_compute_is_inbound_blocked",
        store=True,
        help="Aggregated inbound block flag (self / ancestor / inventory). "
        "Use this for condition evaluation, not 'Block Stock Entrance' "
        "directly.",
    )
    is_outbound_blocked = fields.Boolean(
        compute="_compute_is_outbound_blocked",
        store=True,
        help="Aggregated outbound block flag (self / ancestor / inventory). "
        "Use this for condition evaluation, not 'Block Stock Exit' directly.",
    )

    # ------------------------------------------------------------------
    # Depends declarations as overridable model methods so child modules
    # can extend the dependency graph without rewriting the decorator.
    # ------------------------------------------------------------------

    @api.model
    def _is_ancestor_inbound_blocked_depends(self):
        return (
            "location_id.block_stock_entrance",
            "location_id.is_ancestor_inbound_blocked",
        )

    @api.model
    def _is_ancestor_outbound_blocked_depends(self):
        return (
            "location_id.block_stock_exit",
            "location_id.is_ancestor_outbound_blocked",
        )

    @api.model
    def _is_inventory_blocked_depends(self):
        return ("parent_path", "company_id")

    @api.model
    def _is_inbound_blocked_depends(self):
        return (
            "block_stock_entrance",
            "no_physical_stock",
            "is_ancestor_inbound_blocked",
            "is_inventory_blocked",
        )

    @api.model
    def _is_outbound_blocked_depends(self):
        return (
            "block_stock_exit",
            "no_physical_stock",
            "is_ancestor_outbound_blocked",
            "is_inventory_blocked",
        )

    # ------------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------------

    @api.depends(lambda self: self._is_ancestor_inbound_blocked_depends())
    def _compute_is_ancestor_inbound_blocked(self):
        for loc in self:
            parent = loc.location_id
            loc.is_ancestor_inbound_blocked = bool(
                parent
                and (parent.block_stock_entrance or parent.is_ancestor_inbound_blocked)
            )

    @api.depends(lambda self: self._is_ancestor_outbound_blocked_depends())
    def _compute_is_ancestor_outbound_blocked(self):
        for loc in self:
            parent = loc.location_id
            loc.is_ancestor_outbound_blocked = bool(
                parent
                and (parent.block_stock_exit or parent.is_ancestor_outbound_blocked)
            )

    @api.depends(lambda self: self._is_inventory_blocked_depends())
    def _compute_is_inventory_blocked(self):
        for loc in self:
            loc.is_inventory_blocked = loc._is_inventory_locked()

    @api.depends(lambda self: self._is_inbound_blocked_depends())
    def _compute_is_inbound_blocked(self):
        for loc in self:
            loc.is_inbound_blocked = (
                loc.block_stock_entrance
                or loc.no_physical_stock
                or loc.is_ancestor_inbound_blocked
                or loc.is_inventory_blocked
            )

    @api.depends(lambda self: self._is_outbound_blocked_depends())
    def _compute_is_outbound_blocked(self):
        for loc in self:
            loc.is_outbound_blocked = (
                loc.block_stock_exit
                or loc.no_physical_stock
                or loc.is_ancestor_outbound_blocked
                or loc.is_inventory_blocked
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _ancestor_location_ids(self, include_self=True):
        """Return ids on the materialized parent_path."""
        self.ensure_one()
        ids = [int(x) for x in (self.parent_path or "").split("/") if x]
        if not include_self:
            ids = [i for i in ids if i != self.id]
        return ids

    def _is_inventory_locked(self):
        """True if an in-progress inventory covers this location (or an
        ancestor) and the relevant company opts in."""
        self.ensure_one()
        company = self.company_id or self.env.company
        if not company.block_location_on_inventory:
            return False
        ancestor_ids = self._ancestor_location_ids(include_self=True)
        if not ancestor_ids:
            return False
        return bool(
            self.env["stock.inventory"]
            .sudo()
            .search_count(
                [
                    ("state", "=", "in_progress"),
                    ("location_ids", "in", ancestor_ids),
                ],
                limit=1,
            )
        )

    def write(self, vals):
        res = super().write(vals)
        # When the outbound block is toggled directly on a location, pin/unpin
        # the reservation lock on the stock in its subtree so blocked quants
        # stop being available for picking (and unblocked ones come back).
        # TODO(?): is_outbound_blocked also flips via ancestors and via the
        # inventory toggle (res.company / stock.inventory triggers). Those
        # paths do not pass through this write and would need to resync the
        # reservation lock too.
        if "block_stock_exit" in vals:
            self.env["stock.quant"].sudo().search(
                [("location_id", "child_of", self.ids)]
            )._resync_outbound_reservation_lock()
        return res

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------

    @api.constrains("block_stock_entrance")
    def _check_block_stock_entrance(self):
        self.filtered("block_stock_entrance")._check_lockdown_against_existing_stock(
            "Block Stock Entrance"
        )

    @api.constrains("no_physical_stock")
    def _check_no_physical_stock(self):
        self.filtered("no_physical_stock")._check_lockdown_against_existing_stock(
            "No Physical Stock"
        )

    def _check_lockdown_against_existing_stock(self, label):
        """Raise if a location to be blocked already contains stock and the
        company has not opted in to allowing that."""
        if not self or self.env.company.allow_lockdown_on_stocked_location:
            return
        self.env["stock.quant"]._unlink_zero_quants()
        stocked = self.filtered("quant_ids")
        if stocked:
            raise UserError(
                self.env._(
                    "Cannot enable '%(label)s' on locations that already "
                    "contain stock: %(locs)s",
                    label=label,
                    locs=", ".join(stocked.mapped("display_name")),
                )
            )
