This module adds rules for advanced reservation / removal strategies.

Rules are applied on a location and its sub-locations.

A rule can exclude quants or locations based on configurable criteria,
and based on the selected quants, apply advanced removal strategies.

The rules have a sequence, which will be respected for the reservation.
So even without filter or advanced removal strategies, we can give a priority to
reserve in a location before another.

The advanced removal strategies are applied on top of the default one (fifo,
fefo, ...).

The included advanced removal strategies are:

* Default Removal Strategy: apply the default configured one (fifo, fefo, ...)
* Empty Bins: goods are removed from a bin only if the bin will be empty after
  the removal (favor largest bins first to minimize the number of operations,
  then apply the default removal strategy for equal quantities).
* Full Packaging: tries to remove full packaging (configured on the products)
  first, by largest to smallest package or based on a pre-selected package
  (default removal strategy is then applied for equal quantities).
* Single lot: tries to remove a single lot.
  This strategy requires to select if a tolerance should be applied on lot selection,
  allowing to select lots with qty higher or lower than qty requested in picking.
  Rules can be applied in sequence, for example, to first check for exact lot qty,
  then for a lot with qty 5% higher than requested, then for a lot with qty 10% higher
  than requested, and so on.

  If lot selected must have same qty as requested, set "Tolerance on = No tolerance";
  otherwise it's possible to select a lot with higher qty (Tolerance on = Upper Limit")
  or lower qty ("Lower Limit"), either in percentage of qty or absolute value.
  Please note that three "No tolerance" or "Upper limit" or "Lower limit" rules.


Examples of scenario:

rules:

* location A: no filter, no advanced removal strategy
* location B: no filter, Empty Bins
* location C: no filter, no  advanced removal strategy

result:

* take what is available in location A
* then take in location B if available, only if bin(s) are emptied
* then take what is available in location C

The module is meant to be extensible, with a core mechanism on which new rules
and advanced removal strategies can be added.
