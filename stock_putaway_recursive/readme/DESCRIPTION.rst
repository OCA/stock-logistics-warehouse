This module applies putaway strategies recursively.

By default Odoo applies a putaway strategy on the destination location of a
stock move and returns the first fixed location it finds on the destination
location of the move.

With this module, if another putaway is defined on the returned fixed location,
it will be applied as well, as will be any other putaway strategy that is
defined on the next destination location that is found.
