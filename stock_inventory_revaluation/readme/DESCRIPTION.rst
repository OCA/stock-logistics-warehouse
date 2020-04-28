If your company runs a perpetual inventory system, you may need to perform
inventory revaluation. A revaluation updates both the inventory
account balance, and the stock value of products.

This module takes three different methods of stock revaluation

- Stock-Move-Specific Valuation (FIFO costing)
- Simple Price Change (standard/average costing)
- Inventory-Total-Value Price Change (standard/average costing)


Stock-Move-Specific Valuation
=============================

Stock-Move-Specific valuation applies if the product is configured for FIFO
costing. In this case, the user selects specific stock moves for which to
change value. A journal entry is created for each stock move on which the
value is changed.


Simple Price Change
===================

A simple price change updates the standard/average cost of the product,
regardless of the available stock. The user specifies a new per-unit price,
and posts the change. A journal entry is created for all stock moves having
positive remaining stock value. The amount of the posted entry is the
difference between the new and old price, multiplied by the quantity available.


Inventory-Total-Value Price Change
==================================

This is a price change, based on total available stock value. It updates the
standard/average cost of the product, based on available stock. The user
specifies a new total value for available stock. The standard/average price
of the product is updated to the new total value divided by the available
quantity. A journal entry is created for all stock moves having positive
remaining stock value. The amount of the posted entry is the difference
between the new and old total value.
