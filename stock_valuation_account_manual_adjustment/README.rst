.. image:: https://img.shields.io/badge/license-AGPLv3-blue.svg
   :target: https://www.gnu.org/licenses/agpl.html
   :alt: License: AGPL-3

=========================================
Stock Inventory Account Manual Adjustment
=========================================

This module shows in the product inventory stock value and the accounting
value, and allows to create accounting adjustment entries to align the
accounting value to match with the inventory stock value.

Configuration
=============

Assign the group 'Stock Valuation Account Manual Adjustments' to the users
that should be allowed to list the valuation discrepancies and to reconcile
them.

Usage
=====

* Go to 'Warehouse / Inventory Control / Real Time Inventory Valuation'

* Filter on 'Valuation Discrepancy != 0.0' using the advanced filter.

* Select the products that you wish to reconcile and press 'More /
  Adjust Stock Valuation Account Discrepancies'.


Known issues / Roadmap
======================

* In order to properly manage the inventory valuation from an accounting
  perspective all journal items created for inventory accounts should
  include the product.

* The price change function of Odoo creates journal entries to the inventory
  account without specifying the product. This is bad because you loose the
  ability to control the inventory valuation from accounting at the level of
  the product. In order to fix this, use the module
  'stock_inventory_revaluation', to be found in the same OCA repository.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-warehouse/issues>`_. In case of
trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.


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
