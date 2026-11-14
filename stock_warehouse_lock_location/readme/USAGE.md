The lock location of a warehouse is shown on the Technical Information tab of
the warehouse (Inventory > Configuration > Warehouses, in debug mode), next to
the quality control location. Like the other warehouse locations, it is read
only.

Move goods to the lock location to lock them, and back to the stock location
to release them. Goods in the lock location or its sub-locations still count
in the quantity on hand, but not in the forecasted report: a delivery whose
goods are only there shows as not available.

Modules exchanging stock with a third party can map its locked stock to this
location through the `wh_lock_stock_loc_id` field of the warehouse.
