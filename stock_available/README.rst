.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Stock available to promise
==========================

This module proposes several options to compute the quantity available to
promise for each product.
This quantity is based on the projected stock and, depending on the
configuration, it can account for various data such as sales quotations or
immediate production capacity.
In case of immediate production capacity, it is possible to configure on which
field the potential is computed, by default Quantity On Hand is used.
This can be configured in the menu Settings > Configuration > Warehouse.

Configuration
=============

By default, this module computes the stock available to promise as the virtual
stock.
To take davantage of the additional features, you must which information you
want to base the computation, by checking one or more boxes in the settings:
`Configuration` > `Warehouse` > `Stock available to promise`.
In case of "Include the production potential", it is also possible to configure
which field of product to use to compute the production potential.

Usage
=====

This module adds a field named `Available for sale` on the Product form.
Various additional fields may be added, depending on which information you
chose to base the computation on.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-warehouse/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
stock-logistics-warehouse/issues/new?body=module:%20
stock_available%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Lionel Sausin (Numérigraphe) <ls@numerigraphe.com>
* many others contributed to sub-modules, please refer to each sub-module's credits

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
