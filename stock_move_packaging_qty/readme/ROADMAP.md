- Since we store done product packaging quantities in the stock move
  lines, we should be able to use this information in quants to provide
  real packaging-based stock data.
- For Odoo 19:
  - Remove t-options="{'widget': 'float'}" in `stock_report_delivery_has_serial_move_line`
    and `report_picking views` because are already a Float number.
