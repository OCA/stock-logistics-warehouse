Extends `stock_inventory_discrepancy` module to also consider cost
discrepancies. In other words, this module adds the capability to show the
cost discrepancy of every line in an inventory adjustment and to block the
inventory adjustment validation (setting it as 'Pending to Approve') when
the discrepancy is greater than an user defined amount threshold.
