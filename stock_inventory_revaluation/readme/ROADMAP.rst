- Known Issue: We can't revalue individual lots/serials if there are multiple
  on the same stock move

  - Version 11 moved the cost from stock.quant to stock.move.  That
    means there is no longer an individual cost assigned to specific
    lots/serials.
  - As a work around, you can internally transfer the lot/serial you want to
    revalue.  This will separate it from the other lots/serials on the
    original inbound stock move.

- Known Issue: It is not possible to cancel inventory revaluations for products
  set with average or standard price.
