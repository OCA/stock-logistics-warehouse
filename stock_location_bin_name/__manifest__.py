# Copyright 2017 Syvain Van Hoof (Okia sprl) <sylvainvh@okia.be>
# Copyright 2016-2019 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Location Bin Name",
    "version": "14.0.1.0.0",
    "author": "BCIM, Okia, Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "summary": "Compute bin stock location name automatically",
    "category": "Stock Management",
    "depends": ["stock_location_zone", "stock_location_position"],
    "data": ["views/stock_location.xml"],
    "installable": True,
    "development_status": "Beta",
    "license": "AGPL-3",
}
