- the stock.quant model in Odoo is used to store the stock levels of products in a warehouse
- say we have 100 widgets in stock, 50 of them are conditioned in packs of 10, and 50 are in packs of 25
- Odoo does not currently support this, moreover modifying the stock.quant model to take into account these
packagings would be a hairy task as it is a core model that is read to/written to in many places
- a simple solution is to create a new model and a computed field on stock.quants that will store this information

This module is especially relevant if you are using some form of connector to another system,
for example something like this :

https://github.com/OCA/wms/pull/762

For which you might want to bypass Odoo's tracking and only use the other WMS's inventory as a single, overriding
source of truth. Then you can enrich data from the other WMS while still keeping Odoo's native functionality
in place.
