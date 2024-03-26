This module will allow you to configure Odoo to create journal entries when
transferring goods between 2 internal locations.

Use cases
=========

* You have an internal location "Manufacture Stock" with all the goods that will
  be used for manufacturing. Goods in this location are considered "Work in
  Progress". On the "Manufacture Stock" location, the type is "Internal" and you
  should force the accounting entries to set the "Work in Progress" account.
* You have some specific locations in your warehouse where you want a separate
  account with the value of all the goods at that location.
