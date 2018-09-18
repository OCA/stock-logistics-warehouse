When packaging is configured on products, this module will take priority over
the removal strategy (fifo, lifo, ...). It will try to reserve full packaging
first, then use the removal strategy.

The module does not use a complete tracking of packages throughout the warehouse
to ensure that it reserves a packaging. It assumes that when a location contains
a quantity above the packaging's quantity, it is a full packaging. It cannot
make the difference between 2 half-empty pallet and 1 full pallet, but in
practice, the situation of 2 opened pallets should rarely happen.

Example:

* Product X is configured with pallets of 100 units.
* Location 1 has 80 units, Location 2 has 100 units.
* Location 1 units were input before Location 2.

Normally, the (fifo) reservation would be:

* 80 units from Location 1
* 20 units from Location 2

Using these rules, the reservation is:

* 100 units from Location 2

When the quantity is not a full packaging, there is no change:

* Product X has pallets of 100 units.
* Location 1 has 80 units, Location 2 has 90 units.
* Location 1 units were input before Location 2.

We will have:

* 80 units from Location 1
* 10 units from Location 2
