Quotations in quantity available to promise
===========================================

This module computes the quoted quantity of each Product, and subtracts it from
the quantity available to promise.

"Quoted" is defined as the sum of the quantities of this Product in
Sale Quotations, taking the context's shop or warehouse into account.

Warning for salespersons
------------------------
If you want to keep salespersons from concluding sales that you may not be able to deliver,
you may block the quotations using the module sale_exceptions_ .
Once this module is installed, go to "Sales > Configuration > Sales > Exceptions rules" and create a new rule using the following code:

.. code-block:: python

    if line.product_id and line.product_id.type == 'product' and line.product_id.immediately_usable_qty > line.product_uom_qty:
        failed=True

.. _sale_exceptions: https://www.odoo.com/apps/modules/8.0/sale_exceptions/

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

Credits
=======

Contributors
------------

* Loïc Bellier (Numérigraphe) <lb@numerigraphe.com>
* Lionel Sausin (Numérigraphe) <ls@numerigraphe.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
