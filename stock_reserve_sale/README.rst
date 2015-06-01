.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Stock Reserve Sale
==================

Allows to create stock reservations for quotation lines before the
confirmation of the quotation. The reservations might have a validity
date and in any case they are lifted when the quotation is canceled or
confirmed.

Reservations can be done only on "make to stock" and stockable products.

The reserved products are subtracted from the virtual stock. It means
that if you reserved a quantity of products which bring the virtual
stock below the minimum, the orderpoint will be triggered and new
purchase orders will be generated. It also implies that the max may be
exceeded if the reservations are canceled.

If you want to prevent sales orders to be confirmed when the stock is
insufficient at the order date, you may want to install the
`sale_exception_nostock` module.

Additionally, if the sale_owner_stock_sourcing module is installed, the owner
specified on the sale order line will be proposed as owner of the reservation.
If you try to make a reservation for an order whose lines have different, you
will get a message suggesting to reserve each line individually. There is no
module dependency: this modules is fully functional even without ownership
management.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/stock-logistics-warehouse/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/stock-logistics-warehouse/issues/new?body=module:%20stock_reserve_sale%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Leonardo Pistone <leonardo.pistone@camptocamp.com>
* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

