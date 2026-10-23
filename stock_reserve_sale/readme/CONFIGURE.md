To decide how much stock is reserved from quotations, go to *Sales \>
Configuration \> Settings* and set the *Stock Reservation Policy* in the
*Quotations & Orders* section:

- *Always reserve the ordered quantity* (default): the quantity to
  reserve defaults to the ordered quantity, even if there is no stock in
  the source location. The missing quantity is reserved when it becomes
  available.
- *Reserve the available quantity*: the quantity to reserve defaults to
  the quantity available in the source location, and cannot exceed it.
- *Reserve only if the full quantity is available*: a line can only be
  reserved for its whole ordered quantity, and only when it is available
  in the source location.

Lines with no quantity to reserve are not reserved.

In the same section, *Reservation Transfers* (enabled by default) groups
the stock reservations of each quotation and source location in a
delivery transfer. When it is disabled, the reservations are created as
stock moves without a transfer.
