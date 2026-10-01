This module lets a product be tracked, throughout the whole stock flow, in
a **secondary unit of measure** alongside its normal one - typically a
count (pieces, boxes) next to a product that is actually measured by
weight or volume. A classic case: fish sold by weight, but an order is
placed for "40 pieces" because each of a fixed number of guests gets
exactly one - the real weight per piece varies, but the piece count must
travel through the whole warehouse route exactly as ordered.

It builds on `product_secondary_unit`'s per-product configuration (the
conversion factor, and the `dependency_type` that decides how the two
quantities relate to each other) and extends it to `stock.move` and
`stock.move.line`, so a secondary quantity can be demanded on a
transfer, counted on its operations, and shown on delivery documents -
not just converted once on the product form.

**Two independent secondary-unit settings live on the product:**

- `secondary_uom_ids` / the sale-facing secondary unit (from
  `product_secondary_unit`) - the one that ends up on `stock.move` /
  `stock.move.line` records for an actual transfer.
- `stock_secondary_uom_id` ("Second unit for inventory", added by this
  module) - purely for the **on-hand quantity display**: pick one of the
  product's secondary units and a "Secondary Unit" smart button appears
  on the product form next to "On Hand", showing the current stock
  quantity converted into it. This is read-only, informational, and
  independent of whatever secondary unit an individual move ends up
  using.

**Why `dependency_type` matters here in particular:** a stock move's
`product_uom_qty` (demand) and a move line's `quantity` (what was
actually done) are two different fields with different needs:

- `dependent`: the secondary quantity is always a factor conversion of
  the primary one, in both directions - fine for informational units
  where nothing needs to survive an inexact conversion.
- `independent`: the secondary quantity is entered on its own and never
  recomputed from the primary one, and vice versa - used when the two
  units don't relate to each other at all.
- `secondary_priority`: the primary quantity is *estimated* from the
  secondary one (like `dependent`), but the secondary one is *never*
  recomputed back from the primary (like `independent`) - this is the
  one built for the fish-by-weight/pieces-by-count case: pieces are the
  real order, weight is only ever a convenience estimate derived from
  them, and must never silently drift because of how much something
  happened to weigh.

For `independent` and `secondary_priority` (together, the
"count-preserving" types), the module makes sure the secondary quantity
survives every stock operation exactly, instead of being silently
re-derived from the primary quantity and losing precision or meaning:

- **Splitting a move for a backorder** carries over exactly what's left
  of the secondary demand (e.g. 40 pieces demanded, 30 actually picked
  -> the backorder is for exactly 10 pieces, never a weight-based
  guess), and keeps the original move's own secondary quantity in sync
  with what was actually processed.
- **Merging moves back together** (e.g. two operations for the same
  product ending up as one line, or a backorder's pushed leg merging
  back into an already-existing move) sums the secondary quantities
  the same way core sums the primary one - core has no notion of this
  field at all, so without this the count would silently be lost on
  every merge.
- **A returned (negative) move absorbed into - or absorbing - an
  existing one** rebalances the secondary quantity the same way core
  rebalances the primary one for that specific code path, which is
  separate from the ordinary merge above.
- **A pull-chain procurement** (e.g. a 2-step reception, or an internal
  make-to-order replenishment) carries the secondary unit forward into
  the next move it creates, the same way the primary quantity already
  does.
- **`secondary_uom_qty_done`**, a new aggregate field on `stock.move`,
  mirrors what core's own `quantity` field does for the primary unit: it
  sums what was actually counted across the move's lines, so other code
  needing "how many pieces were actually done" doesn't have to
  re-derive that sum ad hoc every time.
- The **delivery slip report** (and any other place aggregating several
  move lines under one row, e.g. different lots of the same product)
  accumulates the secondary quantity across them instead of only
  showing the last line processed.
