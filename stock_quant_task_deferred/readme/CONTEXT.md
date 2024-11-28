- In Odoo, product quantities are regularily reorganized:
  - when opening the product stock from product form
  - when unpacking products

This implies a lot of stock quants are deleted if you have a lot
of stock operations and users in parallel.

That can causes some DB locks.
