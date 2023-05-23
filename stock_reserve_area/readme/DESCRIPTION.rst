Allows to create reservation areas to manage stock globally on them.
In pickings that move a product out of the source location area,
before making the reservation in the location, the product needs to be available
and reserved in the area.

One location can be inside more than one area as long as the areas are concentric.
For example, there can be a Company level reserve area, inside of it an area for WH1 and inside
an area for Stock. Then, WH/Stock location will be inside  of these three areas at the same time.

The field "Area Reserved Availability" of moves, indicates the quantity that the
system has been able to reserve in all areas (the minimum reserved in the moves' areas).

Use case example:

You have customer demand in WH, and yet you don't want to necessary reserve the stock for that demand in a particular location upfront.
The delivery orders would place demand on WH/Output for example, where there's no stock.

Then, the warehouse people can decide to fulfill that demand later by organizing pickings from WH/Stock to WH/Output.

However, if you try to do that without this module, you cannot guarantee to the customer of a particular sales order that they will get the products they ordered.

With this module, as soon as the delivery order is created, an area level reservation (typicall area will be the whole warehouse) will take place, regardless if the local reservation has taken place yet.
That way we guarantee that new orders will not 'steal' from the previous ones.
