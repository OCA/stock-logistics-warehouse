.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================
Stock history with operations
=============================
Odoo lets advanced users browse the history of the stock by pressing the button "Traceability" on the serial number/lot form, or the "Quant history" button on the quant form.

Unfortunately the standard only presents the associated stock moves, which is a problem because the actual locations can be different: when executing the transfer, stock workers may select any of the sub-locations though various means (automatic reservations, automatic putaway strategies, manual entry).

In order to improve the traceability, this module presents a detailed report containing:

* the details of the Pack Operations involved in the Stock Move, if it was part of a Transfer (delivery order, receipt, internal move)   
* the plain Stock Moves, if the move was made on its own (direct move entry, manufacturing order...)
 
Usage
=====

The improved views are accessible in the following places:

* Warehouse (and most other apps) > Product > form view > button "Detailed traceability"
* Warehouse (and most other apps) > Configuration > Product Variants > form view > button "Detailed traceability"
* Warehouse > Traceability > Serial Number/Lot > form view > button "Detailed traceability"
* Warehouse > Traceability > Quants > form view > button "Detailed traceability"

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/8.0

Known issues
============

This module may mask the changes made by other modules in the traceability views, because it replaces the action of the traceability buttons.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/oca-stock-logistics-warehouse/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/stock-logistics-warehouse/issues/new?body=module:%20stock_quant_manual_assign%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Lionel Sausin <ls@numerigraphe.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
