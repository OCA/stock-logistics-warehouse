This modules improves the way the volume is computed on a stock.move by
taking into account the volume of the potential product packaging
that can be picked to fulfill the move.

The potential packaging that can be picked for a move are computed by the
module *stock_packaging_calculator*. Thanks to this module we can compute the
best distribution of the packaging to uses to fulfill a specific quantity of a
product. (This information is important for the picking operators to minimize
the number of manipulations to do. Even if this information is not available
into the Odoo UI, The *Shopfloor* addon takes advantage of it to propose
the best picking strategy to the user).

By default the volume information is not available on the product packaging.
Hopefully the module *product_packaging_dimension* provides this information.

Since the volume information is not a mandatory field on the product packaging
when we ask for the best distribution of the packaging, packaging without volume
information are ignored. In this way we ensure that the volume of the packaging
is only taken into account when it's relevant otherwise we fallback on the
volume of the products.
