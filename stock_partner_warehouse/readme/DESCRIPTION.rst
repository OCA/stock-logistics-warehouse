This module add a field in res_partner's model to allow to assign a warehouse directly on a partner.
If there is no warehouse set to the partner, it will take automatically the parent's warehouse.
for example, in case of each customer should be supplied by specific warehouse.

See also :
- stock_sale_partner_warehouse (in https://github.com/OCA/stock-logistics-warehouse)
- fieldservice_partner_warehouse (in https://github.com/OCA/field-service)
