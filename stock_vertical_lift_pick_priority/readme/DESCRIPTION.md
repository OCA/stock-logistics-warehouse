On a vertical lift shuttle, the pick screen proposes the move lines of the
most urgent transfers first (see the "Pick urgent transfers first" setting of
`stock_vertical_lift`). This is only relevant when the transfer processed on
the shuttle is itself the urgent one.

In most warehouses, the shuttle feeds an intermediate location: the goods are
picked from the shuttle by an internal transfer (a replenishment), then
delivered by a separate outgoing transfer. The urgency belongs to the
delivery, not to the replenishment.

This module sorts the pick operations by the urgency of the deliveries waiting
for the goods:

- When the replenishment move is chained to outgoing moves (make to order),
  the urgency comes from these outgoing moves.
- Otherwise (make to stock, e.g. orderpoints), the urgency comes from the
  outgoing moves of the same product in the same warehouse.

The most urgent delivery is the one with the highest priority, then the
earliest scheduled date, like Odoo's own reservation order. Move lines without
any waiting delivery keep the order of `stock_vertical_lift`.

Skipped lines still come after the others, oldest skip first. When the
priority of a delivery is raised, the skipped lines waiting for it are
proposed again right away.
