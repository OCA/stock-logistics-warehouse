.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Stock Inventory Discrepancy
===========================

Adds the capability to show the discrepancy of every line in an inventory and
to block the inventory validation (setting it as 'Pending to Approve') when the
discrepancy is greater than a user defined threshold.

Only new group "Validate All inventory Adjustments" will be able to force the
validation of those blocked inventories. By default Stock manager will belong
to this group. In addition, Stock Users can validate inventories under the
threshold now.


Configuration
=============

You can configure the threshold as described below:

#. Go to "Inventory > Warehouse Management" > Warehouses" or to "Inventory >
   Warehouse Management" > Locations".
#. Modify the "Maximum Discrepancy Rate Threshold" either in a Warehouse or
   in a location. If set to 0.0 the threshold is disabled.

Usage
=====

If you configured a "Maximum Discrepancy Rate Threshold".

* When validating an Inventory Adjustment if some line exceed the Discrepancy
  Threshold the system will set the inventory's state to 'Pending to Approve'
  and show the quantity of lines that exceed the threshold.
* If both WH and location thresholds are configured, the location one has
  preference.
* The user with "Validate All inventory Adjustments" rights can force the
  validation of an inventory pending to approve.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/9.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-warehouse/issues>`_. In case of
trouble, please check there if your issue has already been reported. If you
spotted it first, help us smash it by providing detailed and welcomed feedback.


Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Lois Rilo <lois.rilo@eficent.com>


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
