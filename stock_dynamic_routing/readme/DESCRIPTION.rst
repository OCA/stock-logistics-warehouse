Standard Stock Routes explain the steps you want to produce whereas the
“Dynamic Routing” defines how operations are grouped according to their final
source and destination location.

This allows for example:

* To parallelize transfers in two locations of a warehouse, splitting
  them in two different operation type
* To define pre-picking (wave) in some sub-locations, then roundtrip picking of
  the sub-location waves

Context for the use cases:

In the warehouse, you have a High-Bay which requires to place goods in a
handover when you move goods in or out of it. The High-Bay contains many
sub-locations.

A product can be stored either in the High-Bay, either in the Shelving zone.

When picking:

When there is enough stock in the Shelving, you expect the moves to have the
usual Pick(Highbay)-Pack-Ship steps. If the good is picked from the High-Bay, you will
need an extra operation: Pick(Highbay)-Handover-Pack-Ship.

This is what this feature is doing: on the High-Bay location, you define
a "routing rule". A routing rule selects a different operation type for the move.
The extra transfer will have the selected operation type, and be added
dynamically, on reservation, before the chain of moves.

When putting away:

A put-away rule targets the High-Bay location.
An operation Input-Highbay is created. You expect Input-Handover-Highbay.

You can configure a dynamic routing for the put-away on the High-Bay Location.
The operation type of the new Handover move will the one of the matching routing rule,
and its destination will be the destination of the operation type.
