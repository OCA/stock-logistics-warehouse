.. image:: https://img.shields.io/badge/license-AGPLv3-blue.svg
   :target: https://www.gnu.org/licenses/agpl.html
   :alt: License: AGPL-3

======================================
Stock Account Change Product Valuation
======================================

If your company runs a perpetual inventory system, changing the
product's costing method or the type of product requires proper readjustments:

Changing the type of product.

* From consumable to stockable: the resulting inventory value will be reset
  to 0, since everything that was received as a stockable was expensed out
  at the time of entering the supplier invoice.

Changing the costing method:

* From standard or average to real: the cost of all the existing quants will
  be reset to the product's standard price.

* From real to standard or average: the standard price of the product
  template will be set to the average unit cost of all the internal quants.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/9.0

Known issues / Roadmap
======================

Pending to do:

* From stockable to consumable: The inventory value should be
  completely removed. Most importantly when you run a perpetual inventory
  (connected with accounting)


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-warehouse/issues>`_. In case of
trouble, please check there if your issue has already been reported. If you
spotted it first, help us smashing it by providing a detailed and welcomed
feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>


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
