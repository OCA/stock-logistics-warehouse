This module backports the new implementation of putaways as in Odoo v.13.

Models `product.putaway` and `stock.fixed.putaway.strat` are not used anymore
and are replaced by `product.putaway.rule` which has a direct relation to
`stock.location`, instead of having a useless intermediate model.

Usability is therefore improved as putaway rules are accessible from Stock
locations, Products or the dedicated menu entry.
