Try on runbot
~~~~~~~~~~~~~

* In Inventory Settings, activate:

  * Storage Locations
  * Multi-Warehouses
  * Multi-Step Routes

The initial setup in the demo data contains locations:

* WH/Stock/Highbay
* WH/Stock/Highbay/Bin 1
* WH/Stock/Highbay/Bin 2
* WH/Stock/Handover

The "Highbay" location (and children) is configured to:

* create a pull routing transfer from Highbay to Handover when
  goods are taken from Highbay (using a new picking type Highbay → Handover)
* create a push routing transfer from Handover to Highbay when
  goods are put to Highbay (using a new picking type Handover → Highbay)

Steps to try the Pull Routing Transfer:

* In the main Warehouse, configure outgoing shipments to "Send goods in output and then deliver (2 steps)"
* Inventory a product, for instance "[FURN_8999] Three-Seat Sofa", add 50 items in "WH/Stock/Highbay/Bay A/Bin 1", and nowhere else
* Create a sales order with 5 "[FURN_8999] Three-Seat Sofa", confirm
* You'll have 3 transfers; a new one has been created dynamically for Highbay -> Handover.

Steps to try the Push Routing Transfer:

* In the "WH/Stock" location, create a Put-Away Strategy with:

  * "[DESK0004] Customizable Desk (Aluminium, Black)" to location "WH/Stock/Highbay/Bay A/Bin 1"
  * "[E-COM06] Corner Desk Right Sit" to location "WH/Stock/Shelf 1"

* Create a new purchase order of:

  * 5 "[DESK0004] Customizable Desk (Aluminium, Black)"
  * 5 "[E-COM06] Corner Desk Right Sit"

* Confirm the purchase
* You'll have 2 transfers:

  * one to move DESK0004 from Supplier → Handover and E-COM06 from Supplier → Shelf 1
  * one waiting on the other to move DESK0004 from Handover → WH/Stock/Highbay/Bay A/Bin 1 (the final location of the put-away)
