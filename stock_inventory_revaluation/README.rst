.. image:: https://img.shields.io/badge/license-AGPLv3-blue.svg
   :target: https://www.gnu.org/licenses/agpl.html
   :alt: License: AGPL-3

===================================
Stock Account Inventory Revaluation
===================================

If your company runs a perpetual inventory system, you may need to perform
inventory revaluation.

You can re-valuate inventory values by:

* Changing the inventory valuation of a specific product. The cost price
  is changed, and the inventory value is recalculated according to the new
  price. In case of real price, you can select on which quants you want to
  change the unit cost.

* Changing the value of the inventory. The quantity of inventory remains
  unchanged, resulting in a change in the price.



Configuration
=============


* Go to *Inventory / Configuration / Products / Product Categories* and
  define, for each category, a Valuation Increase Account and a Valuation
  Decrease Account. These accounts will be used as contra-accounts to the
  Stock Valuation Account during the inventory re-valuation.

* Users willing to access to the Inventory Revaluation menu should be
  members of the group "Manage Inventory Valuation and Costing Methods".


Usage
=====

* Go to *Inventory / Inventory Control / Inventory Revaluation / Products*
  to create a new Inventory Revaluation. For products set with average or
  standard price and real-time valuation, go to the Product form and use the
  link to change the standard price.

* In order to post the inventory revaluation for multiple items at once,
  select the records in the tree view and go to
  *More / Post Inventory Revaluations*.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/8.0

Known issues / Roadmap
======================

* A negative quant can be revaluated, but can also ultimately be merged with
  a positive quant. In that case, the associated revaluation quant record
  will be removed. In a future version a chatter could be added to the stock
  inventory revaluation, and this kind of action would be logged for better
  traceability.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock_account_inventory_revaluation/issues>`_. In
case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed `feedback <https://github.com/OCA/154/issues/new?body=module:%20
stock_account_inventory_revaluation%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20..
.%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Eficent Business and IT Consulting Services S.L. <contact@eficent.com>


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
