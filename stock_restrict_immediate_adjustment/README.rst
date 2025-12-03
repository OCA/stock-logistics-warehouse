===================================
Stock Restrict Immediate Adjustment
===================================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fstock--logistics--warehouse-lightgray.png?logo=github
    :target: https://github.com/OCA/stock-logistics-warehouse/tree/18.0/stock_restrict_immediate_adjustment
    :alt: OCA/stock-logistics-warehouse

|badge1| |badge2| |badge3|

This module prevents accidental immediate stock adjustments from the "Stock On Hand" 
view that is accessible from product cards and inventory reports.

**Problem**

In standard Odoo, when users click on the "On Hand" quantity button from a product 
or access the inventory report, they can immediately change stock quantities just by 
typing a new value. The change is applied instantly without any confirmation step, 
making it very easy to accidentally modify inventory.

**Solution**

This module disables inline editing in the stock quant tree view, forcing users to:

1. Use the "Inventory Adjustments" menu where they must explicitly click "Apply" to 
   confirm changes
2. Prevents accidental stock modifications from quick views
3. Ensures proper traceability of all inventory adjustments

**Table of contents**

.. contents::
   :local:

Usage
=====

After installing this module:

* When you click on "On Hand" quantity from a product card, the quant list view 
  will be read-only
* When you access the inventory report, direct editing is disabled
* Users must go to Inventory > Operations > Inventory Adjustments to make stock 
  changes with proper confirmation

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/stock-logistics-warehouse/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Authors
-------

* ForgeFlow

Contributors
------------

- `ForgeFlow <https://www.forgeflow.com>`__:

  - Joan Sisquella <joan.sisquella@forgeflow.com>

Maintainers
-----------

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/stock-logistics-warehouse <https://github.com/OCA/stock-logistics-warehouse/tree/18.0/stock_restrict_immediate_adjustment>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
