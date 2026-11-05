Extends `stock_reserve_sale` to allow making stock reservations for
quotation lines of kit products (bills of materials of type *Kit*).

When a kit line is reserved, a stock reservation is created for each
component of the kit, for the quantity of the component needed to make
the quantity of the kit to reserve.

In the reservation wizard, the quantity available of a kit is computed
from the quantities of its components available in the source location,
so the *Stock Reservation Policy* also applies to kits.
