.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Partner Location Auto Create
============================

This module allows to create locations automatically when creating a partner.
One use case of this feature is to allow a company not only to manage the stocks
in its own warehouses, but also the warehouses of its suppliers.
For example, an hatchery manages farms. Each farm is a partner and has its own inventory.
The hatchery doesn't own the farms but manages their stocks.

Whether the partner is a customer, a supplier or both, the proper locations will be created and
the fields property_stock_customer and property_stock_supplier will be filled automatically.

The modules also adds a button on the partner form to view the related locations.

Installation
============

To install this module, you just need to select the module and ensure yourself dependencies are available.

Configuration
=============

* Add users to the group "Sales Pricelists" or "Purchase Pricelists" to view the stock location properties on the partner view.
* In the company form, select the default customer and supplier locations. This will set the default parent locations for the partner locations.

Usage
=====

To use this module, you need to :

- Create a partner
- Click on the locations button and add specific locations for the partner

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/153/8.0


Known issues / Roadmap
======================

Credits
=======

Module developed and tested with Odoo version 8.0

Contributors
------------

* David DUFRESNE <david.dufresne@savoirfairelinux.com>
* Sandy CARTER <sandy.carter@savoirfairelinux.com>
* Adriana IERFINO <adriana.ierfino@savoirfairelinux.com>
* Bruno JOLIVEAU <bruno.joliveau@savoirfairelinux.com>

Maintainer
----------

Odoo Community Association

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
