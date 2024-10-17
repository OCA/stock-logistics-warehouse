In older versions of `stock_inventory`, the lines in the `stock.inventory` model were not part of the `stock.quant` model.
In those versions, a line was created for every product found by the inventory adjustment group, regardless of whether
the product was in stock or not.

Currently, the lines of the model use Odoo's base `stock.quant` model. This means that if you select any configuration
that includes a product without a `stock.quant` record, no line is created for that product. This behavior disrupts the
intended functionality of the `stock_inventory` module, which is supposed to group all lines into a single record. If the
lines do not exist, they are not displayed, making the adjustment process meaningless.
