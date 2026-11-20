Go to *Inventory > Operations > External Inventory Reports*.

Open a report, review its lines (*Mark Reviewed*) or apply the external
quantities to the Odoo stock (*Apply Stock Overwrite*), then mark the report
processed once every line is reviewed or applied.

Developers of an integration create the report (warehouse, lines with
`external_product_code`, `external_lot_name`, `stock_type`, `external_qty`)
and run its comparison, `process_comparisons_and_alerts()` (in jobs with
`stock_external_inventory_report_queue`). *Run Comparison* runs it again from
the report.
They can override:

- `stock.external.inventory.report.line._normalize_stock_type(stock_type)`,
  when the external system names the stock types otherwise;
- `stock.external.inventory.report._get_discrepancy_threshold()`: the
  variance amount above which a line is a discrepancy (100.0 by default).
