**Update Unit Price of Specific Lots/Serials**

- Go to Inventory -> Reporting -> Valuation
- Choose Group By -> Lot/Serial
- Expand the row for a lot/serial that is configured for Specific Identification
  Valuation
- Click the + (plus) button
- Complete the Revaluation Wizard

**Feature Demonstration:**

In the following, we demonstrate two cases in which this module changes the way
stock valuation is performed by the system.  To set up these cases, we need to:

1. Configure a category for Specific Identification Valuation
1. Create a product, assigned to that category, with serial tracking enabled

**Specific identification of purchased value:**

1. Purchase one unit of the product on its own purchase order, serialized as SN01
1. Purchase a second unit of the product on a separate purchase order, with a
   different cost, serialized as SN02
1. Sell the second unit of the product (SN02) before selling the first (SN01)

With FIFO costing method, the outbound move for the sold unit would take the
value of the first unit purchased.  This module changes the behavior so that the
value of the outbound move will be that of the second unit (SN02).

**Specific identification of value changes:**

1. Manufacture two units of the product, serialized as SN03 and SN04
1. Revalue one of the serialized units
1. Sell the revalued unit

With FIFO costing method, the outbound move for the sold unit would be valued as
the total valuation for
value of the first unit purchased.  This module changes the behavior so that the
value of the outbound move will be that of the second unit (SN02).
