# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def _block_location_on_inventory(self):
        """Return the subset of ``self`` whose effective company has the
        ``block_location_on_inventory`` setting enabled. Inventories not in
        this subset have no impact on stock.location.is_inventory_blocked and
        must not trigger recomputes for their own location subtree."""
        return self.filtered(
            lambda inv: (inv.company_id or inv.env.company).block_location_on_inventory
        )

    def _affected_inventory_lock_locations(self):
        if not self.location_ids:
            return self.env["stock.location"]
        return self.env["stock.location"].search(
            [("id", "child_of", self.location_ids)]
        )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        relevant = records._block_location_on_inventory()
        if relevant:
            affected_locs = relevant._affected_inventory_lock_locations()
            affected_locs._compute_is_inventory_blocked()
        return records

    def write(self, vals):
        relevant = self._block_location_on_inventory()
        track = bool(relevant and {"state", "location_ids"} & set(vals))
        before_locs = self.env["stock.location"]
        if track:
            before_locs = relevant._affected_inventory_lock_locations()
        res = super().write(vals)
        if track:
            after_locs = relevant._affected_inventory_lock_locations()
            affected_locs = before_locs | after_locs
            affected_locs._compute_is_inventory_blocked()
        return res

    def unlink(self):
        relevant = self._block_location_on_inventory()
        locs = (
            relevant._affected_inventory_lock_locations()
            if relevant
            else self.env["stock.location"]
        )
        res = super().unlink()
        if locs:
            locs._compute_is_inventory_blocked()
        return res
