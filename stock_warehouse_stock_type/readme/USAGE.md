This is a technical module. On `stock.warehouse`:

- `_get_stock_types()`: the stock types, each with the warehouse field
  holding its location and the error to raise when it is not set;
- `_get_stock_type_location(stock_type, required=False)`: the location of a
  stock type;
- `_get_location_stock_type(location)`: the stock type of a location.

To add a stock type, override `_get_stock_types()`, e.g.:

    def _get_stock_types(self):
        res = super()._get_stock_types()
        res["blocked"] = {
            "wh_location_field": "my_blocked_location_id",
            "missing_message": self.env._("No blocked location..."),
        }
        return res
