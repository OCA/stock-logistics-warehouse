This module extends the stock.lot model to manage customer and vendor warranty dates for
serial-tracked products.

* Vendor warranty: When a product is received from a vendor, the vendor warranty start and end dates
are automatically computed based on the receipt date and the vendor warranty settings on the product.
If the product is returned to the vendor, the warranty dates are cleared.

* Customer warranty: When a product is delivered to a customer, the customer warranty start and end
dates are automatically computed based on the delivery date and the product’s customer warranty settings.
If the product is returned by the customer, the warranty dates are cleared, and they are recalculated if
the product is sold again.

This module also allows users to manually edit warranty dates directly on the lot/serial form,
with all changes logged in the chatter for full traceability.

The logic is the most basic logic for warranty management, and has been implemented in different hook methods,
allowing other modules to easily override or extend warranty management, such as managing returns in RMA or
repair workflows.
