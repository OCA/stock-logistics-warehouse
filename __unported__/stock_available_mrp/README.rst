Consider the production potential is available to promise
=========================================================

This module takes the potential quantities available for Products in account in
the quantity available to promise, where the "Potential quantity" is the
quantity that can be manufactured with the components immediately at hand.

Known issues
============

The manufacturing delays are not taken into account : this module assumes that
if you have components in stock goods, you can manufacture finished goods
quickly enough.
To avoid overestimating, **only the first level** of Bill of Materials is
considered.

Roadmap
-------

* include all levels of BoM, using `bom_explode`. @gdgellatly gave an example
  of how to do it here: https://github.com/OCA/stock-logistics-warehouse/pull/5#issuecomment-66902191
    Ideally, we will want to take manufacturing delays into account: we can't
    promiss goods to customers if they want them delivered earlier that we can
    make them
* add an option (probably as a sub-module) to consider all raw materials as
  available if they can be bought from the suppliers in time for the
  manufacturing.

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
