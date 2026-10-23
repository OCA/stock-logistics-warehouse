Glue module between **stock_reserve_sale** and **sale_stock_picking_blocking**.
**stock_reserve_sale** releases the stock reservations of a quotation when it is
confirmed, so that the delivery order takes over the reserved stock, but no
delivery order is created while the sales order has a delivery block. This module
keeps the reservations of orders confirmed with a **Delivery Block Reason**, and
releases them when the block is removed, right before the delivery order is
created and reserves that stock.
