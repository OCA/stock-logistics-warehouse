**Known Issues:**

- In order to have different prices for different serialized units of the same
  product, create a separate purchase order for each serial number
- When returning a delivery of multiple serialized units of the same product,
  each serial number must be returned separately
- Negative stock quantities are not allowed for products with specific
  identification valuation
- Modifying completed moves with multiple lots/serials is not allowed

**Future Improvements:**

- Inherit and modify the wizard `stock.valuation.layer.revaluation`, rather than
  creating a new wizard `stock.valuation.layer.lot.revaluation`
- Inherit and modify the product `_run_fifo()` method, rather than creating the
  lot `_run_out_spec_ident` method
