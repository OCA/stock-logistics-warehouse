.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================
Stock Removal Location by Priority
==================================

This module adds a removal priority field on stock locations.
This priority applies when removing a product from different stock locations
and the incoming dates are equal in both locations.

Configuration
=============

You can configure the removal priority as follows:

#. Go to "Inventory > Configuration > Settings"
#. In 'Location & Warehouse' section, mark the "Removal Priority" option.

NOTE: To be able to view this option you need to have already marked:

#. Manage several locations in "Warehouses and Locations usage level" option.
#. Advanced routing of products using rules in "Routing" option.

Usage
=====

To use this module, you need to:

#. Go to "Inventory > Configuration > Warehouse Management > Locations"
#. In each Location form, in the Logistics section, put a Removal Priority.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/10.0


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

* Miquel Raïch <miquel.raich@eficent.com>


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
