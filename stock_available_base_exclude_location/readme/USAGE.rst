In new module, inherit from "stock.exclude.location.mixin" model on
the wanted model.

Then, when querying for product availability, add to context the key
"excluded_location_ids" with your model "stock_excluded_location_ids"
property.
