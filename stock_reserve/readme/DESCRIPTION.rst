Allows to create stock reservations on products.

Each reservation can have a validity date, once passed, the reservation
is automatically lifted.

The reserved products are substracted from the virtual stock. It means
that if you reserved a quantity of products which bring the virtual
stock below the minimum, the orderpoint will be triggered and new
purchase orders will be generated. It also implies that the max may be
exceeded if the reservations are canceled.

If ownership of stock is active in the stock settings, you can specify the
owner on the reservation.
