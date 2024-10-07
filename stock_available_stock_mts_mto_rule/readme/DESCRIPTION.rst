This is a glue module between `stock_mts_mto_rule` and `stock_avaiable`.
It will use the `immediately_usable_qty` field to compute the split for the
mts mto rule, instead of the `virtual_available` value.
