#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import OrderedDict
from psycopg2 import OperationalError

from odoo import api, models, registry
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, \
    float_round


class ProcurementGroup (models.Model):
    _inherit = 'procurement.group'

    def _get_orderpoint_domain(self, company_id=False):
        domain = super()._get_orderpoint_domain(company_id=company_id)
        domain = expression.AND((
            domain,
            [
                ('is_other_availability', '=', False),
            ],
        ))
        return domain

    def _get_orderpoint_other_availability_domain(self, company_id=False):
        domain = super()._get_orderpoint_domain(company_id=company_id)
        domain = expression.AND((
            domain,
            [
                ('is_other_availability', '=', True),
            ],
        ))
        return domain

    # Keep this method as similar to super as possible, to ease maintenance
    # pylint: disable=invalid-commit
    # flake8: noqa: E501,E128
    @api.model
    def _procure_orderpoint_other_availability_confirm(self, use_new_cursor=False, company_id=False):
        """Trigger orderpoints based also on another product availability.

        Cannot override in a clean way the orderpoint logic,
        so just copy and change a few lines.
        Note that this method is only called for the rules
        having `is_other_availability` enabled (see `_get_orderpoint_domain`).
        """
        if company_id and self.env.user.company_id.id != company_id:
            self = self.with_context(company_id=company_id, force_company=company_id)
        OrderPoint = self.env['stock.warehouse.orderpoint']
        # This has changed: get the domain only for the new type of rules
        domain = self._get_orderpoint_other_availability_domain(company_id=company_id)

        orderpoints_noprefetch = OrderPoint.with_context(prefetch_fields=False).search(domain,
            order=self._procurement_from_orderpoint_get_order()).ids
        while orderpoints_noprefetch:
            if use_new_cursor:
                cr = registry(self._cr.dbname).cursor()
                self = self.with_env(self.env(cr=cr))
            OrderPoint = self.env['stock.warehouse.orderpoint']

            orderpoints = OrderPoint.browse(orderpoints_noprefetch[:1000])
            orderpoints_noprefetch = orderpoints_noprefetch[1000:]

            # Calculate groups that can be executed together
            location_data = OrderedDict()

            def makedefault():
                return {
                    'products': self.env['product.product'],
                    # This is added
                    'other_products': self.env['product.product'],

                    'orderpoints': self.env['stock.warehouse.orderpoint'],
                    'groups': []
                }

            for orderpoint in orderpoints:
                key = self._procurement_from_orderpoint_get_grouping_key([orderpoint.id])
                if not location_data.get(key):
                    location_data[key] = makedefault()
                location_data[key]['products'] += orderpoint.product_id
                # This is added
                location_data[key]['other_products'] += orderpoint.other_availability_product_id

                location_data[key]['orderpoints'] += orderpoint
                location_data[key]['groups'] = self._procurement_from_orderpoint_get_groups([orderpoint.id])

            for location_id, location_data in location_data.items():
                location_orderpoints = location_data['orderpoints']
                product_context = dict(self._context, location=location_orderpoints[0].location_id.id)
                # This is added: context for availability from other location
                other_location = location_orderpoints[0].other_availability_location_id or location_orderpoints[0].location_id
                other_product_context = dict(self._context, location=other_location.id)

                substract_quantity = location_orderpoints._quantity_in_progress()

                for group in location_data['groups']:
                    if group.get('from_date'):
                        product_context['from_date'] = group['from_date'].strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        # This is added
                        other_product_context['from_date'] = group['from_date'].strftime(DEFAULT_SERVER_DATETIME_FORMAT)

                    if group['to_date']:
                        product_context['to_date'] = group['to_date'].strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        # This is added
                        other_product_context['to_date'] = group['to_date'].strftime(DEFAULT_SERVER_DATETIME_FORMAT)

                    product_quantity = location_data['products'].with_context(product_context)._product_available()
                    # This is added
                    other_product_quantity = location_data['other_products'].with_context(other_product_context)._product_available()

                    for orderpoint in location_orderpoints:
                        try:
                            # This is added: get availability for other product
                            other_product_virtual = other_product_quantity[orderpoint.other_availability_product_id.id]['virtual_available']

                            op_product_virtual = product_quantity[orderpoint.product_id.id]['virtual_available']

                            # This is changed: also compare other product availability
                            if other_product_virtual is None or op_product_virtual is None:
                                continue
                            # This has changed: only minimum quantity
                            # for other product triggers the rule
                            other_not_available = float_compare(
                                other_product_virtual,
                                orderpoint.other_availability_qty,
                                precision_rounding=orderpoint.product_uom.rounding) <= 0
                            if other_not_available:
                                qty = orderpoint.product_max_qty - op_product_virtual
                                remainder = orderpoint.qty_multiple > 0 and qty % orderpoint.qty_multiple or 0.0

                                if float_compare(remainder, 0.0, precision_rounding=orderpoint.product_uom.rounding) > 0:
                                    qty += orderpoint.qty_multiple - remainder

                                if float_compare(qty, 0.0, precision_rounding=orderpoint.product_uom.rounding) <= 0:
                                    continue

                                qty -= substract_quantity[orderpoint.id]
                                qty_rounded = float_round(qty, precision_rounding=orderpoint.product_uom.rounding)
                                if qty_rounded > 0:
                                    values = orderpoint._prepare_procurement_values(qty_rounded, **group['procurement_values'])
                                    try:
                                        with self._cr.savepoint():
                                            self.env['procurement.group'].run(orderpoint.product_id, qty_rounded, orderpoint.product_uom, orderpoint.location_id,
                                                                              orderpoint.name, orderpoint.name, values)
                                    except UserError as error:
                                        self.env['stock.rule']._log_next_activity(orderpoint.product_id, error.name)
                                    self._procurement_from_orderpoint_post_process([orderpoint.id])
                                if use_new_cursor:
                                    cr.commit()

                        except OperationalError:
                            if use_new_cursor:
                                orderpoints_noprefetch += [orderpoint.id]
                                cr.rollback()
                                continue
                            else:
                                raise

            try:
                if use_new_cursor:
                    cr.commit()
            except OperationalError:
                if use_new_cursor:
                    cr.rollback()
                    continue
                else:
                    raise

            if use_new_cursor:
                cr.commit()
                cr.close()

        return {}

    @api.model
    def _procure_orderpoint_confirm(self, use_new_cursor=False, company_id=False):
        res = super()._procure_orderpoint_confirm(
            use_new_cursor=use_new_cursor, company_id=company_id,
        )
        self._procure_orderpoint_other_availability_confirm(use_new_cursor=use_new_cursor, company_id=company_id)
        return res
