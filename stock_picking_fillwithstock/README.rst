.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================
Stock Picking Fill with stock
=============================

On a draft picking, add a button to fill with moves lines for all products in
the source destination. This allows to create a picking to move all the content
of a location. If some quants are not available (i.e. reserved) the picking
will be in partially available state and reserved moves won't be listed in the
operations.

Usage
=====

Use barcode interface to scan a location and create an empty picking. Then use
the fill with stock button.

Credits
=======

Contributors
------------

* Jacques-Etienne Baudoux <je@bcim.be>
