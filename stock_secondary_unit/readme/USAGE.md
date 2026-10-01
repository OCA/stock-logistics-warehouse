## Displaying stock on hand in a secondary unit

1. On a product, go to *Inventory tab \> Secondary unit* and choose
   which of the product's configured secondary units should be used
   for the on-hand display ("Second unit for inventory").
2. A "Secondary Unit" smart button appears on the product form (next
   to "On Hand"), showing the current stock quantity converted into
   that unit. This is purely informational: it does not affect any
   transfer.

## Demanding and counting a secondary quantity on a transfer

1. On a transfer's operations (the move lines list, or a move's own
   detail form when *Detailed Operations* is enabled), the
   *Secondary Qty* and its unit are editable columns/fields (needs the
   "Units of Measure" feature enabled, `uom.group_uom`).
2. What happens when the secondary quantity is entered depends on the
   product's secondary unit `dependency_type`:
   - `dependent`: entering either quantity recomputes the other
     through the conversion factor.
   - `independent` / `secondary_priority`: the secondary quantity is
     entered on its own; for `secondary_priority` the primary quantity
     is estimated from it, but never the other way round once a
     secondary quantity has actually been set.

## Validating a transfer that doesn't match the secondary demand exactly

For a count-preserving secondary unit (`independent` or
`secondary_priority`), if what was actually counted is less than
demanded and a backorder gets created:

- The backorder is created for **exactly** what's left of the secondary
  demand (e.g. 40 pieces demanded, 30 counted -> the backorder demands
  exactly 10 pieces) - never a proportional estimate derived from
  whatever the primary quantity (e.g. weight) happened to be.
- The original, now-done transfer keeps its secondary quantity in sync
  with what was actually counted, not the original demand.

If instead more was counted than demanded, the move's own demand is
left untouched by this module alone - see the receiving module/process
(e.g. a reception-discrepancy or over-processing reconciliation
feature) for how a peixospalamos-style deployment handles that case; it
is out of scope for this module by itself.

## Returns

When a return (a move with a negative quantity) gets merged back into
an existing move - or absorbs one, if the return is larger - the
secondary quantity is rebalanced the same way the primary one is: the
surviving move's secondary quantity reflects the net effect of the
return, not just whatever it already had before the return was
processed.

## Chained transfers (multi-step routes, make-to-order replenishment)

When a transfer is part of a pull chain (e.g. the "Input -> Stock" leg
of a 2-step reception, or an internal make-to-order move), whatever
secondary unit and quantity is set on it is carried forward into the
next transfer created for that chain - the destination move doesn't
start without one.

## Delivery documents

The delivery slip report shows the secondary quantity and unit next to
the primary one for every line, both for a picking still being
processed and once it is done. When several move lines end up
aggregated onto a single report row (e.g. different lots of the same
product), their secondary quantities are summed, not just the last one
read.
