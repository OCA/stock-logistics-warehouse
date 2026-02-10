This module extends the inventory adjustment flow to allow users to choose
the inventory loss (counterpart) location when applying adjustments.

By default, Odoo uses the **Inventory Location** configured on the product
category (`property_stock_inventory`). With this module installed, the
"Apply All" wizard presents an optional **Inventory Location** field. When
set, all adjustments in the batch use the selected location instead of the
product category default.
