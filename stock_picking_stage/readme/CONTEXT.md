This module has been created to be able to track operations running on a picking.
We can consider that as a substate of the picking:
- By default, we have some states on a picking:
  - draft
  - waiting
  - confirmed
  - assigned
  - done
  - cancelled
- Using this module, we can add some substate to the picking:
  - `stock.picking.state` --> `assigned`:
    - `stock.picking.stage_id` -->  `new order`
    - `stock.picking.stage_id` -->  `preparing`
    - `stock.picking.stage_id` -->  `processed`

This approach is more flexible than using only the `state` field of the picking.
