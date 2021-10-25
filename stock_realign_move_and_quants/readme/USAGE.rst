This module adds a wizard in the menu

  Inventory > Configuration > Align Stock Moves and Quants

This wizard is only accessible to admin user.

In this wizard, enter the date from which you want to fix the alignement.
Good dates are the first ever move (default) or the switch to Odoo 12.

Upon validation, the wizard

- computes the stock based on the stock move lines,
- fixes the quants with that value (cf server logs),
- opens an inventory with all the fixed product.

Both columns, theoretical quantity and verified quantity display the same
value. This is normal, theoretical quantity is based on the new fixed
quants and verified quantity is set by the wizard based on the moves.

This is a good time to make an actual inventory on those product and
fix the values in the inventory.

Finally, click on validate to finish the process.

This module also adds a fix to quant to prevent blocking the pickings
in the future.
