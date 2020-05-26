
Basic module providing an helper method to calculate the quantity of product by packaging.

Imagine you have the following packagings:

* Pallet: 1000 Units
* Big box: 500 Units
* Box: 50 Units

and you have to pick from your warehouse 2860 Units.

Then you can do:

    >>> product.product_qty_by_packaging(2860)

    [(2, "Pallet"), (1, "Big Box"), (7, "Box"), (10, "Units")]

With this you can show a proper message to warehouse operators to quickly pick the quantity they need.
