.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================================
Sensible limits on minimum stock rule processing
================================================

This module modifies minimum stock rule processing to not reorder products
that are inactive or obsolete, unless for satisfying outstanding orders.

Procurement can even be totally prohibited by unchecking the Purchase Allowed
(purchase_ok) flag on the product.

Usage
=====

If you want to prevent any purchase procurement for a product, uncheck the
Purchase is Allow flag on the product.

If you only want to procure enough products to satisfy outstanding requests,
make a product obsolete or inactive.

Known issues / Roadmap
======================

At present there are no known issues.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association:
  `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Ronald Portier <rportier@therp.nl>

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
