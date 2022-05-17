# Copyright (C) 2021 Open Source Integrators (https://www.opensourceintegrators.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "checkout_count" in counters:
            values["checkout_count"] = (
                request.env["stock.location.content.check"].search_count(
                    self._get_checkouts_domain()
                )
                if request.env["stock.location.content.check"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )
        return values

    def _get_checkouts_domain(self):
        return [("state", "=", "confirmed"), ("user_id", "=", request.env.user.id)]

    @http.route(
        ["/my/checkouts", "/my/checkouts/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_checkouts(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        Checkout = request.env["stock.location.content.check"]
        domain = self._get_checkouts_domain()
        searchbar_sortings = {}

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        # count for pager
        checkout_count = Checkout.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/checkouts",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=checkout_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager
        checkouts = Checkout.search(
            domain, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_checkout_history"] = checkouts.ids[:100]

        values.update(
            {
                "date": date_begin,
                "checkouts": checkouts.sudo(),
                "page_name": "checkout",
                "pager": pager,
                "default_url": "/my/checkouts",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render(
            "portal_stock_location_content_template.checkout_portal", values
        )

    @http.route(
        ["/my/checkouts/<int:checkout_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_checkout_detail(self, checkout_id, access_token=None, **kw):
        try:
            checkout_sudo = self._document_check_access(
                "stock.location.content.check", checkout_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        values = self._checkout_get_page_view_values(checkout_sudo, access_token, **kw)
        return request.render(
            "portal_stock_location_content_template.checkout_tmaplate_view", values
        )

    def _checkout_get_page_view_values(self, checkout_sudo, access_token, **kwargs):
        values = {
            "page_name": "checkout",
            "checkout": checkout_sudo,
        }
        return self._get_page_view_values(
            checkout_sudo, access_token, values, "my_checkout_history", False, **kwargs
        )

    @http.route("/checkout/complete", type="json", auth="public", website=True)
    def checkout_complete(self, stock_content=None, vals=None, **post):
        if not vals:
            vals = []

        if stock_content:
            stock_content = request.env["stock.location.content.check"].browse(
                int(stock_content)
            )
        for val in vals:
            line = request.env["stock.location.content.check.line"].browse(
                int(val.get("id"))
            )
            line.sudo().write(
                {
                    "counted_qty": val.get("counted_qty"),
                    "replenished_qty": val.get("replenished_qty"),
                }
            )

        stock_content.sudo().action_complete()
        return True
