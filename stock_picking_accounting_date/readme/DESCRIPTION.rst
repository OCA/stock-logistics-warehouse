This module adds accounting date in picking and pass the value to accounting date
of SVL's journal entry.

Background
~~~~~~~~~~

When a user makes the transfer for the products with "real time"
inventory valuation, effective date in transfer couldn't be selected.

And Accounting date for stock valuation journal entry will be the same with effective date.
So, for the users who want to specify each transfer's actual accounting date needs to reset to draft
manually and change acocunting date. This module intends to get rid of this
inconvenience by adding accounting date in transfer and pass to journal entry.
