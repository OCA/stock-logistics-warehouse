General
~~~~~~~

In Inventory Settings, you must have:

 * Storage Locations
 * Multi-Warehouses
 * Multi-Step Routes

Locations
~~~~~~~~~

Additional configuration parameters are added in Locations:

* Sub-locations of a location with the "Is a Vertical Lift View Location"
  activated are considered as "Shuttles". A shuttle is a vertical lift shelf.
* Sub-locations of shuttles are considered as "Trays", which is a tier of a
  shuttle. When a tray is created, a tray type must be selected. When saved, the
  tray location will automatically create as many sub-locations - called
  "Cells" - as the tray type contains.
* The tray type of a tray can be changed as long as none of its cell contains
  products. When changed, it archives the cells and creates new ones as
  configured on the new tray type.

Tray types
~~~~~~~~~~

Tray types can be configured in the Inventory settings.
A tray type defines how much cells a tray can hold. It is a square or rectangle
matrix of n cols * m rows.

Vertical Lift Shuttles
~~~~~~~~~~~~~~~~~~~~~~

The Shuttles are the Vertical Lift Trays. One Shuttle entity has to be created
in Odoo for each physical shuttle. Depending of the subsidiary addons installed
(eg. Kardex), different options may be required (host address, ...). The base
addon only includes shuttles of kind "simulation" which will not send orders to
the hardware.

Put-away configuration
~~~~~~~~~~~~~~~~~~~~~~

If you want to use put-away in the vertical lift, the Receipts must have the
vertical lift view as destination. E.g. create put-away rules on the products
so when they arrive in WH/Stock, they are stored in WH/Stock/Vertical Lift. On
the put-away screen, when scanning the tray type to store, the destination will
be updated with an available cell of the same tray type in the current shuttle.

Barcodes
~~~~~~~~

The operations allowed in the screen for the vertical lift (save, release, skip)
can be triggered using a barcode. For this, print the barcodes contained in the
folder 'images'.
