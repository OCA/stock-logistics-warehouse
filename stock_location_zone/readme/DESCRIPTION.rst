This module introduces Zone concept on stock locations to allow better
classification of stock locations in a warehouse.

Locations are then classified by location kinds that could be:

* Zone: locations that are flagged as being zones. Zones are subdivisions of the warehouse for splitting picking operations. A picking operator work in a zone and can pick from any location of the zone.
* Area: locations with children that are part of a zone. Areas are subdivisions of the warehouse for put-away operations. Each area has storage characteristics and strategy, e.g. area for pallets, shelf for boxes...
* Bin: locations without children that are part of a zone
* Stock: internal locations whose parent is a view
* Other: any other location
