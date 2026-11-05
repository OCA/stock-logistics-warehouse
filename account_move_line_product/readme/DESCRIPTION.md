In Odoo 19.0, product information is already available on journal items, but
grouping by product is not provided out of the box, and product and quantity
fields are either hidden by default or not displayed on journal entry lines.

This module:

- Adds a "Group By Product" filter in the Journal Items search view.
- Displays product and quantity by default in the Journal Items list view.
- Displays product and quantity on the Journal Items tab of Journal Entries.

This is especially relevant in perpetual inventory for inventory-related
account moves.
