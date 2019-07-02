Route explains the steps you want to produce whereas the “picking routing
operation” defines how operations are grouped according to their final source
and destination location.

This allows for example:

* To parallelize picking operations in two locations of a warehouse, splitting
  them in two different picking type
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
a "routing operation". A routing operation is based on a picking type.
The extra operation will have the selected picking type, and the new move
will have the source destination of the picking type.

When putting away:

A put-away rule targets the High-Bay location.
An operation Input-Highbay is created. You expect Input-Handover-Highbay.

You can configure a routing operation for the put-away on the High-Bay Location.
The picking type of the new Handover move will the routing operation selected,
and its destination will be the destination of the picking type.
