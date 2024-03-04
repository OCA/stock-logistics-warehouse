Allows to create stock reservations for quotation lines before the
confirmation of the quotation. The reservations might have a validity
date and in any case they are lifted when the quotation is canceled or
confirmed.

Reservations can be done only on "make to stock" and stockable products.

The reserved products are subtracted from the virtual stock. It means
that if you reserved a quantity of products which bring the virtual
stock below the minimum, the orderpoint will be triggered and new
purchase orders will be generated. It also implies that the max may be
exceeded if the reservations are canceled.

If you want to prevent sales orders to be confirmed when the stock is
insufficient at the order date, you may want to install the
`sale_exception_nostock` module.

Additionally, if the sale_owner_stock_sourcing module is installed, the owner
specified on the sale order line will be proposed as owner of the reservation.
If you try to make a reservation for an order whose lines have different, you
will get a message suggesting to reserve each line individually. There is no
module dependency: this modules is fully functional even without ownership
management.
