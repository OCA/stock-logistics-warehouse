As the number of packing space is usually limited, if someone starts to prepare
an order by picking it in a zone, all other related picking in the other zones
should be of a higher priority. This should make a "started" order a priority
for all.

This module adds an option "Raise priority when partially available" on
operation types.

When the option is set on an operation type, the first time a packing operation
is made partially available (goods have been moved for instance from a picking),
all the other moves that will bring goods for the same packing transfer have
their priority raised to "Very Urgent". If the moves that bring goods to the
packing transfer involves a chain of several moves, all the moves of the chain
have their priority raised.
