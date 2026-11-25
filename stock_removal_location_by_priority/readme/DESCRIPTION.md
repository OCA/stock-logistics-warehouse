This module adds a removal priority field on stock locations. This
priority applies when removing a product from different stock locations
and the incoming dates are equal in both locations.

The removal priority is only taken into account with the FIFO and LIFO
removal strategies. Any other strategy (Closest Location, Least
Packages, FEFO...) keeps its standard behaviour and ignores the removal
priority.
