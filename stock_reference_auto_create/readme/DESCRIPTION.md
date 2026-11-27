This module allows the system to propose automatically new stock
references during the procurement run.

This capability is important when you want to make sure that all the
stock moves resulting from a procurement run will never be mixed with
moves from other references in stock transfers.

The stock transfers resulting from the procurement run will only contain
stock moves created in that run.

This module was called `procurement_auto_create_group` up to version 18.0.
Rename the module in the database before upgrading it (for example with
`openupgradelib.openupgrade.update_module_names`); its migration script then
renames the field `auto_create_group` to `auto_create_reference`.
