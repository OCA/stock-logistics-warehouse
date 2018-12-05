The aim of this module is to mark internal locations where no product should transit.
Indeed, in complex warehouse setups, we may have a complicated tree of internal locations with parent locations only used to create the hierarchy of the internal locations.
We may want to avoid to put stock on these parent internal locations since they are not physical locations, they just represent a zone of the warehouse.
Theses locations must have *Location Type* set to *Internal Location* because they belong to a warehouse (they can't be configured with *Location Type* set to *View*, cf `Odoo bug #26679 <https://github.com/odoo/odoo/issues/26679>`_). With this module, you will be able to enable a new option *Block stock entrance* for these locations.
