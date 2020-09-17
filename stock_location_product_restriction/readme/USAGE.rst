By default, Odoo allows you to put items of any product into the same location.
This behaviour remains the one by default once the addon is installed.
Once installed, you can specify at any level of the stock location hierarchy
if you want to restrict the usage of the location to only items of the same
product. This property is inherited by all the children locations while you
don't specify an other specific value on a child location. The constrains only
applies location by location.

Once a location is configured to only contains items of the same product, the
system will prevent you to move items of any others products into a location
that already contains product items. A new filter into the tree view of the
stock locations will also allow you to find all the location where this new
restriction is violated.
