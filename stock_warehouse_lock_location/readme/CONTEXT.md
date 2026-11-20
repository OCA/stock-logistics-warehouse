Some warehouses, typically run by a warehouse management system (WMS) or a
logistics provider, keep stock in a locked state: the goods are on hand, but
must not be picked for deliveries until they are released (e.g. blocked by a
quality hold, or reserved for a specific use).

Odoo has a quality control location on warehouses, but no location for locked
goods. Like any internal location under the warehouse view location, such a
location would also be counted by the forecasted report as available for the
deliveries of the warehouse.
