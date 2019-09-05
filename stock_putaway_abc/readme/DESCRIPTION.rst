This module implements ABC chaotic storage putaways.

Instead of defining putaway with a fixed location for product or product
category, this module allows to define an ABC preference for product or product
category on the product putaway form.

When such a putaway is applied, it will look recursively for a stock location
without children whose ABC classification matches the ABC priority of the
putaway.

e.g. for a putaway with B priority, it will look on children locations
for a B location. If no B location is found, it will look for a C. If no C
location is found, it will look for an A. Finally, if no location matches, it
will return the stock location where the putaway is applied.
