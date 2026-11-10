The pull list checks the stock situation at the given location and
calculates the shortfall quantities (quantity needed to cover all needs)
for products. Procurements can be created for these shortfall
quantities.

In Odoo 20.0 the stock rule lookup prefers the rules of the procurement
company, so the module now uses the company of the selected location
(falling back to the current company) instead of the user's default
company to find rules and run procurements.
