from collections import OrderedDict

from odoo import _, http
from odoo.http import request
from odoo.osv.expression import OR

from odoo.addons.portal.controllers.portal import (
    CustomerPortal,
    get_records_pager,
    pager as portal_pager,
)


class PortalProduct(CustomerPortal):
    def _get_product_searchbar_sorting(self):
        return {
            "date": {"label": _("Create Date"), "order": "create_date desc"},
            "name": {"label": _("Name"), "order": "name"},
            "default_code": {"label": _("SKU"), "order": "default_code"},
        }

    def _get_product_searchbar_filters(self):
        return {
            "all": {"label": _("All"), "domain": []},
        }

    def _get_searchbar_inputs(self):
        return {
            "all": {"input": "all", "label": _("Search in All")},
            "default_code": {"input": "default_code", "label": _("Search in SKU")},
            "name": {"input": "display_name", "label": _("Search in Product Name")},
        }

    def _get_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ("name", "all"):
            search_domain = OR([search_domain, [("name", "ilike", search)]])
        if search_in in ("default_code", "all"):
            search_domain = OR([search_domain, [("default_code", "ilike", search)]])
        return search_domain

    def _prepare_portal_layout_values(self):
        values = super(PortalProduct, self)._prepare_portal_layout_values()
        Product = request.env["product.product"]
        values.update(access_to_products=Product.check_product_portal_access())
        return values

    def _prepare_home_portal_values(self, counters):
        values = super(PortalProduct, self)._prepare_home_portal_values(counters)
        if "product_count" in counters:
            Product = request.env["product.product"]
            values.update(product_count=len(Product.get_portal_products(False)))
        return values

    def _product_get_page_view_values(self, product, access_token, **kwargs):
        values = {"page_name": "product", "product": product}
        history = request.session.get("my_products_history", [])
        values.update(get_records_pager(history, product.sudo()))
        return self._get_page_view_values(
            product, access_token, values, "my_products_history", False, **kwargs
        )

    @http.route(
        ["/my/products", "/my/products/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_products(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        filterby=None,
        search=None,
        search_in="all",
        **kw
    ):
        values = self._prepare_portal_layout_values()
        if not values.get("access_to_products", False):
            return request.redirect("/my/home")
        Product = request.env["product.product"]

        searchbar_sorting = self._get_product_searchbar_sorting()
        searchbar_filters = self._get_product_searchbar_filters()
        searchbar_inputs = self._get_searchbar_inputs()

        domain = []

        if not sortby:
            sortby = "date"
        order = searchbar_sorting[sortby]["order"]
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]["domain"]
        if search and search_in:
            domain += self._get_search_domain(search_in, search)
        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        product_count = len(Product.get_portal_products(domain))

        pager = portal_pager(
            url="/my/products",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "search_in": search_in,
                "search": search,
                "filterby": filterby,
                "sortby": sortby,
            },
            total=product_count,
            page=page,
            step=self._items_per_page,
        )

        products = Product.get_portal_products(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )

        request.session["my_products_history"] = products.ids[:100]

        values.update(
            {
                "date": date_begin,
                "products": products,
                "page_name": "product",
                "pager": pager,
                "default_url": "/my/products",
                "searchbar_sortings": searchbar_sorting,
                "search_in": search_in,
                "search": search,
                "filterby": filterby,
                "searchbar_inputs": searchbar_inputs,
                "sortby": sortby,
                "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
                "date_end": date_end,
            }
        )
        return request.render("stock_available_portal.portal_my_products", values)

    @http.route(
        ["/my/products/<int:product_id>"], type="http", auth="user", website=True
    )
    def portal_product_page(self, product_id, access_token=None, **kw):
        Product = request.env["product.product"]
        product = Product.get_portal_products([("id", "=", product_id)])
        if Product.check_product_portal_access() and product:
            values = self._product_get_page_view_values(product, access_token, **kw)
            return request.render("stock_available_portal.portal_my_product", values)
        return request.redirect("/my/home")
