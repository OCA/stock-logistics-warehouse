If you are using a database with demo data, you can give a try
to the following scenario to understand how it works.

The demo data created by the module contains:

A product: Funky Socks

3 Locations:

* Stock / Zone A / Bin A1: 200 Funky socks
* Stock / Zone B / Bin B1: 100 Funky socks
* Stock / Zone C / Bin C1: 100 Funky socks

3 Reservation Rules, in the following order

* Zone A must have full quantities
* Zone B
* Zone C

2 Delivery Orders:

* Origin: Outgoing shipment (reservation rules demo 1)
* Origin: Outgoing shipment (reservation rules demo 2)

Scenario:

* Activate Storage Locations and Multi-Warehouses
* You can open Inventory > Configuration > Stock Reservation Rules to activate
  and see the rules (by default in demo, the rules are created inactive)
* Open Transfer: Outgoing shipment (reservation rules demo 1)
* Check availability: it has 150 units, as it will not empty Zone A, it will not
  take products there, it should take 100 in B and 50 in C (following the rules
  order)
* Unreserve this transfer (to test the second case)
* Open Transfer: Outgoing shipment (reservation rules demo 2)
* Check availability: it has 250 units, it can empty Zone A, it will take 200 in
  Bin A1 and 50 in Bin B1.
* If you want to explore further, you can add a custom domain to exclude rules
  (for instance, a product category will not use Zone B).
