Review the stock reported by an external system (a WMS, a 3PL, a count
file...) against the Odoo stock, and apply it.

An *External Inventory Report* holds the external stock of a warehouse: one
line per product code, lot and stock type, with the external quantity. The
comparison resolves each line to a product, lot and location (from the stock
type, see `stock_warehouse_stock_type`), reads the Odoo quantity on hand and
computes the quantity and value differences. Activities are scheduled for the
lines above the discrepancy threshold, the products without cost and the
products not found.

The stock manager reviews the lines and can overwrite the Odoo stock with the
external quantities (inventory adjustment). A new report makes the previous
pending ones of its warehouse obsolete; obsolete reports can't be changed.

The reports are created by the module integrating the external system.
