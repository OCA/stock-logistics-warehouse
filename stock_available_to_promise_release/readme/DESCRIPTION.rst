Currently the reservation is performed by adding reserved quantities on quants,
which is fine as long as the reservation is made right after the order
confirmation. This way, the first arrived, first served principle is always
applied. But if you release warehouse operations in a chosen order (through
deliver round for example), then you need to be sure the reservations are made
in respect to the first arrived first served principle and not driven by the
order you choose to release your operations.

Allow each delivery move to mark a quantity as virtually reserved. Simple rule
would be first ordered, first served. More complex rules could be implemented.

When the reservation of a picking move occurs, the quantity that is reserved is
then based on the quantity that was promised to the customer (available to promise):

* The moves can be reserved in any order, the right quantity is always reserved
* The removal strategy is computed only when the reservation occurs. If you
  reserve order 2 before order 1 (because you have/want to deliver order 2) you
  can apply correctly fifo/fefo.

  * For instance order 1 must be delivered in 1 month, order 2 must be delivered now.
  * Virtually lock quantities to be able to serve order 1
  * Reserve remaining quantity for order 2 and apply fefo

* Allow to limit the promised quantity in time. If a customer orders now for a
  planned delivery in 2 months, then allow to not lock this quantity as
  virtually reserved
* Allow to perform reservations jointly with your delivery rounds planning.
  Reserve only the quants you planned to deliver.
