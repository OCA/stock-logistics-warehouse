# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = "stock.quant"

    # Outbound reservation lock: for a quant in an outbound-blocked location we
    # hold ``reserved_quantity == quantity`` so the stock is not available for
    # picking (available = quantity - reserved = 0) and is removed from the
    # forecast figures natively. The genuine reservation is parked here so it
    # can be restored when the location is unblocked.
    lock_real_reserved = fields.Float(default=0.0)
    is_outbound_reservation_locked = fields.Boolean(default=False)

    def _check_location_outbound_blocked(self):
        # Outbound block: a quant cannot leave a location that is outbound
        # blocked. @api.constrains sees only the post-write location_id, so the
        # source must be checked before the value is overwritten.
        for quant in self:
            if quant.location_id.is_outbound_blocked:
                raise ValidationError(
                    self.env._(
                        "The location %(location)s is blocked for outbound "
                        "and the product %(product)s cannot be moved out of it"
                    )
                    % {
                        "location": quant.location_id.display_name,
                        "product": quant.product_id.display_name,
                    }
                )

    def write(self, vals):
        if "location_id" in vals:
            self._check_location_outbound_blocked()
        # TODO(?): a direct write({"reserved_quantity": ...}) bypasses
        # _update_reserved_quantity and would desync the outbound reservation
        # lock (reserved_quantity vs lock_real_reserved). Do we enforce that all
        # reserved_quantity changes go through the _update_reserved_quantity
        # funnel, or accept that direct writes are not lock-aware?
        return super().write(vals)

    # Raise an error when trying to change a quant
    # which corresponding stock location is blocked
    @api.constrains("location_id")
    def check_location_blocked(self):
        for record in self:
            if record.location_id.is_inbound_blocked:
                raise ValidationError(
                    self.env._(
                        "The location %(location)s is blocked and can "
                        "not be used for moving the product %(product)s"
                    )
                    % {
                        "location": record.location_id.display_name,
                        "product": record.product_id.display_name,
                    }
                )

    # ------------------------------------------------------------------
    # Outbound reservation lock

    # TODO: the reservation pinning should be a dedicated module
    def _is_outbound_reservation_pinned(self):
        """Whether this quant's reserved_quantity is currently held at quantity
        for the outbound lock. Single source of truth for the pinned state, so
        callers never read the storage field directly."""
        self.ensure_one()
        return self.is_outbound_reservation_locked

    def _pin_outbound_reservation(self):
        """Hold reserved_quantity at quantity, parking the genuine reservation
        in lock_real_reserved, so the stock is unavailable for picking."""
        for quant in self:
            if quant._is_outbound_reservation_pinned():
                continue
            quant.lock_real_reserved = quant.reserved_quantity
            quant.reserved_quantity = quant.quantity
            quant.is_outbound_reservation_locked = True

    def _unpin_outbound_reservation(self):
        """Restore the genuine reserved_quantity so core logic operates on the
        real numbers."""
        for quant in self:
            if not quant._is_outbound_reservation_pinned():
                continue
            quant.reserved_quantity = quant.lock_real_reserved
            quant.lock_real_reserved = 0.0
            quant.is_outbound_reservation_locked = False

    def _resync_outbound_reservation_lock(self):
        """Pin/unpin each quant to match its location's outbound-blocked
        state."""
        for quant in self:
            if quant.location_id.is_outbound_blocked:
                quant._pin_outbound_reservation()
            else:
                quant._unpin_outbound_reservation()

    @api.model
    def _update_reserved_quantity(
        self,
        product_id,
        location_id,
        quantity,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        inner = self.with_context(skip_outbound_reservation_lock=True)
        quants = inner._gather(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
        pinned = quants.filtered(lambda q: q._is_outbound_reservation_pinned())
        # Normal behavior unless some targeted quants are pinned by the outbound
        # reservation lock (and the lock is not bypassed via context): then
        # divert the change to the genuine reserved value (lock_real_reserved)
        # and keep reserved_quantity pinned at quantity so the stock stays
        # unavailable.
        if self.env.context.get("skip_outbound_reservation_lock") or not pinned:
            return super()._update_reserved_quantity(
                product_id,
                location_id,
                quantity,
                lot_id=lot_id,
                package_id=package_id,
                owner_id=owner_id,
                strict=strict,
            )
        # Expose the genuine reserved values, let core apply the delta, then
        # re-pin so picking still sees nothing available.
        quants._unpin_outbound_reservation()
        res = super(StockQuant, inner)._update_reserved_quantity(
            product_id,
            location_id,
            quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
        # Re-pin the same quants we unpinned, rather than re-gathering: a child
        # module could override _gather to conditionally drop quants, which
        # would leave some unpinned. .exists() guards against a zero quant that
        # super may have unlinked.
        quants.exists()._resync_outbound_reservation_lock()
        return res

    @api.model
    def _clean_reservations(self):
        # The reconciler compares reserved_quantity against the real move-line
        # reservations and would otherwise erase the pinned inflation. Expose
        # the genuine reserved values, reconcile, then re-pin.
        locked = self.sudo().search([("is_outbound_reservation_locked", "=", True)])
        locked._unpin_outbound_reservation()
        res = super()._clean_reservations()
        self.sudo().search(
            [("location_id.is_outbound_blocked", "=", True)]
        )._resync_outbound_reservation_lock()
        return res
