This module introduces Zone concept on stock locations to allow better
classification of stock locations in a warehouse.

Locations are then classified by location kinds that could be:

* Zone: locations that are flagged as being zones
* Area: locations with children that are part of a zone
* Bin: locations without children that are part of a zone
* Stock: internal locations whose parent is a view
* Other: any other location
