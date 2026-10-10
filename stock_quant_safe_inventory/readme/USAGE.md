To prevent inventory of quants being processed you must check the
`Stock quant no inventory if being picked` parameter into the stock
settings panel. (stock -> configuration -> settings)

In the inventory list view (stock -> operations -> physical inventory), a
truck icon is displayed next to the counted quantity of quants for which some
quantities are currently being picked. Clicking on it opens the related move
lines. The inventory of these quants can only be applied once these transfers
are validated.

Odoo already detects when the on hand quantity changes after the counted
quantity has been set (e.g. a transfer validated in the meantime) and asks
the user how to resolve the conflict before applying the inventory.
