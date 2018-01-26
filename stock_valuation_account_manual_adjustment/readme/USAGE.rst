To use this module, you need to:

* Go to 'Inventory / Inventory Control / Perpetual Inventory Valuation'

* Filter using the filter 'Valuation Discrepancy' which filters out
  products with no Valuation Discrepancy.

* Select the products that you wish to reconcile and press 'Action /
  Adjust Stock Valuation Account Discrepancies'.

* You can provide Valuation Increase/Decrease Contra-Account. Otherwise the
  application will attempt to use the ones defined in the product category.
  Note that when the adjustment implies an increase of the valuation of your
  inventory (thus a debit), the account 'Valuation Increase Contra-Account')
  will be used in the credit side of the journal entry. And when the
  inventory valuation is going to decrease (credit), the account 'Valuation
  Decrease Contra-Account' will be used in the debit side of the journal
  entry. Typically the 'Valuation Increase Contra-Account' will be of type
  'Equity' and 'Valuation Decrease Contra-Account' will be of type 'Expense'.
