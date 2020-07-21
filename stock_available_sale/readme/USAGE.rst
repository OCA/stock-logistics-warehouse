Warning for salespersons
~~~~~~~~~~~~~~~~~~~~~~~~
If you want to keep salespersons from concluding sales that you may not be able
to deliver, you may block the quotations using the module sale_exception_.
Once this module is installed, go to "Sales > Configuration > Sales >
Exceptions rules" and create a new rule using the following code:

.. code-block:: python

    if (line.product_id and line.product_id.type == 'product' and
            line.product_id.immediately_usable_qty > line.product_uom_qty):
        failed=True

.. _sale_exception: https://github.com/OCA/sale-workflow/tree/10.0/sale_exception

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/10.0
