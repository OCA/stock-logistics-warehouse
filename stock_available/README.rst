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

Credits
=======

Contributors
------------

* Lionel Sausin (Numérigraphe) <ls@numerigraphe.com>
* Sodexis <sodexis@sodexis.com>
* many others contributed to sub-modules, please refer to each sub-module's credits

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
