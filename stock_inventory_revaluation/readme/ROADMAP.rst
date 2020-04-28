- Known Issue: We can't revalue individual lots/serials if there are multiple
  on the same stock move

  - Version 11 moved the cost from stock.quant to stock.move.  That
    means there is no longer an individual cost assigned to specific
    lots/serials.
  - As a work around, you can internally transfer the lot/serial you want to
    revalue.  This will separate it from the other lots/serials on the
    original inbound stock move.

- Known Issue: Actual resulting stock value may differ slightly from that
  specified by the user.  This can result when the Product Price
  decimal precision is low, and there is a large quantity of product to
  revaluate. For example:

  - If we have 147 units on hand, and the precision for Product Price is 2
    digits
  - When we specify a new value of 750, the actual value applied is 749.70
  - At full precision, 750 / 147 = 5.102041, but the product cost gets
    rounded to 5.10, and 5.10 * 147 = 749.70
  - As a work around, you can change the decimal precision setting for Product
    Price to have a greater number of digits
