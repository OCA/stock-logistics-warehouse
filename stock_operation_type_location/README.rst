.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3
    
=============================
Stock Operation Type Location
=============================

This module was written to extend the functionality of the stock operations 
which allows users to filter destination and source locations when adding products.


Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/OCA/stock-logistics-warehouse
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *Stock Operation Type Location*
6.  Install the module

Usage
=====

To use this module, you need to:

1.  Go to menu *Warehouse -> Configuration -> Types of Operation*
2.  Then click on one of picking type name so get into form view
3.  Under *Default Source Location*, there will be a new field named *Allowed Source Location*
4.  If *Allowed Source Location* is filled, then the *Source Location* when adding products in stock operation 
    will be filtered according to the location of this field
5.  Under *Default Destination Location*, there will be a new field named *Allowed Destination Location*
6.  If *Allowed Destination Location* is filled, then the *Destination Location* when adding products in stock 
    operation will be filtered according to the location of this field

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
stock_operation_type_location%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Michael Viriyananda <viriyananda.michael@gmail.com>

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
