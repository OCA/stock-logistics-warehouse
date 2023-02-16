.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================
Stock Orderpoint Manual Procurement
===================================

This module allows users to manually start procurements from the list of
reordering rules, based on the quantity that is recommended to be procured.

Configuration
=============

If you want users to be able to change the recommended quantity to procure,
you should assign them to the security group 'Change quantity in manual
procurements from reordering rules', under 'Settings / Users / Users'.

Usage
=====

Go to 'Inventory > Master Data > Reordering Rules' and review the quantity
recommended to be procured. You can now start the procurement for a single or a
list of reordering rules.

The recommended quantity to procure is adjusted to the procurement unit of
measure indicated in the reordering rule.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-warehouse/issues>`_. In case of trouble, please
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
* Lois Rilo Antelo <lois.rilo@eficent.com>
* Bhavesh Odedra <bodedra@opensourceintegrators.com>

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
