Imagine you have the following packagings:

* Pallet: 1000 Units
* Big box: 500 Units
* Box: 50 Units

and you have to pick from your warehouse 2860 Units.

Then you can do:

    .. code-block::

        >>> product.product_qty_by_packaging(2860)

        [
            {"id": 1, "qty": 2, "name": "Pallet"},
            {"id": 2, "qty": 1, "name": "Big box"},
            {"id": 3, "qty": 7, "name": "Box"},
            {"id": 100, "qty": 10, "name": "Units"},
        ]

With this you can show a proper message to warehouse operators to quickly pick the quantity they need.

Optionally you can get contained packaging by passing `with_contained` flag:


    .. code-block::

        >>> product.product_qty_by_packaging(2860, with_contained=True)

        [
            {"id": 1, "qty": 2, "name": "Pallet", "contained": [{"id": 2, "qty": 2, "name": "Big box"}]},
            {"id": 2, "qty": 1, "name": "Big box", "contained": [{"id": 3, "qty": 10, "name": "Box"}]},
            {"id": 3, "qty": 7, "name": "Box", "contained": [{"id": 100, "qty": 50, "name": "Units"}]},
            {"id": 100, "qty": 10, "name": "Units", "contained": []},},
        ]
