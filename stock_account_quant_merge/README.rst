.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Stock Account Quant merge
=========================

This module is an extension of "stock_quant_merge", and adds the cost as a
criteria to merge quants.

Odoo splits quants each time a reservation is done: this module makes Odoo
merge them back if they still meet the following requirements:

* same product
* same serial number/lot
* same location
* same package
* same unit cost
* same incoming date

The restriction to only merge quants that have been received in the same
date, with the the same cost is very important when the product is defined
with the real costing method.

Usage
=====

The merge is done automatically when a reservation is undone. No user intervention is needed.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-warehouse/issues>`_. In case of
trouble, please check there if your issue has already been reported. If you
spotted it first, help us smashing it by providing a detailed and welcomed
feedback.


Credits
=======

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
