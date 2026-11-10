In order to have a pertinent value for the computed volume, the
dimension fields must be set on all the products.

The computed volume depends on the move state.

- If the move is done, the volume is the volume for the qty done.
- If the move is cancelled or draft waiting, the volume is the volume
  for the qty to do.
- if the move is available or partially available, the volume is the
  volume for the reserved quantity.

When the module is installed on an existing database, the volume field
is only computed for the stock moves of pickings not yet processed. The
moves in a cancelled or done picking are not updated to avoid to freeze
the database for a long time during the upgrade process if it contains a
lot of stock moves and pickings.
