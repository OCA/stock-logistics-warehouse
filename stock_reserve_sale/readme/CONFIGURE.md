To decide how much stock is reserved from quotations, go to *Sales \>
Configuration \> Settings* and set the *Stock Reservation Policy* in the
*Quotations & Orders* section:

- *Always reserve the ordered quantity* (default): the reservation is
  created for the ordered quantity even if there is no stock in the
  source location. The missing quantity is reserved when it becomes
  available.
- *Reserve the available quantity*: only the quantity that is available
  in the source location is reserved.
- *Reserve only if the full quantity is available*: a line is reserved
  only when its whole quantity is available in the source location.

With the last two policies, lines without available stock are not
reserved, and an error is raised if none of the selected lines can be
reserved.

In the same section, *Reservation Transfers* (enabled by default) groups
the stock reservations of each quotation and source location in a
delivery transfer. When it is disabled, the reservations are created as
stock moves without a transfer.
