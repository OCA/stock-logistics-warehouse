.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

======================
Stock Reorder Forecast
======================

Allows to predict date when stock levels will reach minimum by
analizying sales volume in a period and therefore to trigger RFQ's ahead
of time

Extends stock to calculate period turnover and  ultimate date of order 
(the date where we reach minimum stock)
This module allows to create RFQ's by checking the product form and 
examining the ultimate purchase value.

The ultimate purchase value is the date we forecast this product will not be
available. It is obtained by calculating the average sales rate of this 
product and predicting at this rate how long will it take for the 
stock to reach 0 at this speed.

The period upon wich we calculate this average rate  be personalized, default is:

TURNOVER_PERIOD = Amount of time to calculate average (default 365)
TURNOVER_AVERAGE = Average sale rate in that period.
Ultimate Purchase = Day in the future where stock should finish at current
rate.

All values are  (period, average) are kept on (in order of importance):
            * Supplier Info
            * Partner
            * Category

if the values are not set on supplier info it will default to values on
partner, if not set on supplier will default to category, if not set anywhere 
will default to Hardcoded values (ir.config.parameters period=365 days).  

The turnover average and the ultimate purchase derived by it are calculated in
bulk by a daily cron job.

==========
Usage
==========

Set on product and/or partner(supplier) and/or product category the values of turnover
period.

Make sure the cron job  "Purchase Proposal Refresh" is activated, launch it
manually the first time in order to have all "ultimate dates" for products
calculated. Set the cron job time/date at a convenient time and frequency, this
job will refresh all stats used for forcasting ultimate purchase date. If you
have a high volume of sales and do frequent resupplies it is advisable to
launch it multiple times a day.


View products to see all products with an ultimate order date, for that
interface you can generate a RFQ to desired date.

You can also view from the partner/supplier form all products ordered by this
partner.



Credits
=======

Contributors
------------

* Giovanni Francesco Capalbo <giovanni@therp.nl> 
* Holger Brunn <hbrunn@therp.nl>
* Hans Van Dijk <hvd400@gmail.com>
* Ronald Portier <rportier@therp.nl>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
