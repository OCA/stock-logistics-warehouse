.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================================
Quotations in quantity available to promise
===========================================

This module computes the quoted quantity of each Product, and subtracts it from
the quantity available to promise.

"Quoted" is defined as the sum of the quantities of this Product in
Sale Quotations, taking the context's shop or warehouse into account.

Usage
=====

Warning for salespersons
------------------------
If you want to keep salespersons from concluding sales that you may not be able to deliver,
you may block the quotations using the module sale_exceptions_ .
Once this module is installed, go to "Sales > Configuration > Sales > Exceptions rules" and create a new rule using the following code:

.. code-block:: python

    if line.product_id and line.product_id.type == 'product' and line.product_id.immediately_usable_qty > line.product_uom_qty:
        failed=True

.. _sale_exceptions: https://www.odoo.com/apps/modules/8.0/sale_exceptions/

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/8.0

Known issues / Roadmap
======================

Changed features
----------------
The quoted quantity is now returned as a positive value, whereas it was returned as a negative value before v8.0.
This change was made to ensure consistency with the standard, which used to present outgoing quantities as negative numbers until v8.0, and now presents them as positive numbers instead.

Removed features
----------------
Previous versions of this module used to let programmers demand to get the quoted quantity in an arbitrary Unit of Measure using the `context`. This feature was present in the standard computations too until v8.0, but it has been dropped from the standard from v8.0 on.
For the sake of consistency the quoted quantity is now always reported in the product's main Unit of Measure too.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-warehouse/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
stock-logistics-warehouse/issues/new?body=module:%20
stock_available_sale%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Loïc Bellier (Numérigraphe) <lb@numerigraphe.com>
* Lionel Sausin (Numérigraphe) <ls@numerigraphe.com>

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
