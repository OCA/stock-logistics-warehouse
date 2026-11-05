This module adds a tier validation process to inventory adjustments
(`stock.inventory`), so that counted quantities update stock only after the
configured reviewers have approved the adjustment.

Once a tier definition exists for inventory adjustments, on-hand quantities can
no longer be applied directly from the quants: the *Apply* button is hidden on
the counting lines, and any other attempt to apply a counted quantity outside a
validated adjustment raises an error. The counted quantities are applied when a
validated adjustment is set to done.
