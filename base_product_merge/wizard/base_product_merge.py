# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA
# @author Guewen Baconnier
# Original code from module base_partner_merge by Tiny and Camptocamp
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

# TODO : create a base_merge module to provide abstractions for merges ?

from osv import fields, osv
from tools.translate import _
import tools


class base_product_merge(osv.osv_memory):
    """
    Merges two products
    """
    _name = 'base.product.merge'
    _description = 'Merges two products'

    _columns = {
    }
    
    _values = {}

    MERGE_SKIP_FIELDS = ['product_tmpl_id']

    def _build_form(self, cr, uid, field_datas, value1, value2):
        formxml = '''<?xml version="1.0"?>
            <form string="%s">
            <separator colspan="4" string="Select datas for new record"/>''' % _('Merge')
        update_values = {}
        update_fields = {}
        columns = {}

        for fid, fname, fdescription, ttype, required, relation, readonly in field_datas:
            if fname in self.MERGE_SKIP_FIELDS:
                continue

            val1 = value1[fname]
            val2 = value2[fname]
            my_selection = []
            size = 24

            if (val1 and val2) and (val1 == val2):
                if ttype in ('many2one'):
                    update_values.update({fname: val1.id})
                elif ttype in ('many2many'):
                    update_values.update({fname: [(6, 0, map(lambda x: x.id, val1))]})
                else:
                    update_values.update({fname: val1})

            if (val1 and val2) and (val1 != val2) and not readonly:
                if ttype in ('char', 'text', 'selection'):
                    my_selection = [(val1, val1), (val2, val2)]
                    size = max(len(val1), len(val2))
                if ttype in ('float', 'integer'):
                    my_selection = [(str(val1), str(val1)), (str(val2), str(val2))]
                if ttype in ('many2one'):
                    my_selection = [(str(val1.id), val1.name),
                                    (str(val2.id), val2.name)]
                if ttype in ('many2many'):
                    update_values.update({fname: [(6, 0, list(set(map(lambda x: x.id, val1 + val2))))]})
                if my_selection:
                    if not required:
                        my_selection.append((False, ''))
                    columns.update({fname: fields.selection(my_selection, fdescription, required=required, size=size)})
                    update_fields.update({fname: {'string': fdescription, 'type': 'selection', 'selection': my_selection, 'required': required}})
                    formxml += '\n<field name="%s"/><newline/>' % (fname,)
            if (val1 and not val2) or (not val1 and val2):
                if ttype == 'many2one':
                    update_values.update({fname: val1 and val1.id or val2 and val2.id})
                elif ttype == 'many2many':
                    update_values.update({fname: [(6, 0, map(lambda x: x.id, val1 or val2))]})
                elif ttype == 'one2many':
                    #skip one2many values
                    pass
                else:
                    update_values.update({fname: val1 or val2})

        formxml += """
        <separator colspan="4"/>
        <group col="4" colspan="4">
            <label string="" colspan="2"/>
            <button special="cancel" string="Cancel" icon="gtk-cancel"/>
            <button name="action_merge" string="Merge" type="object" icon="gtk-ok"/>
        </group>
        </form>"""
        return formxml, update_fields, update_values, columns

    def check_resources_to_merge(self, cr, uid, resource_ids, context):
        """ Check validity of selected resources.
         Hook for other checks
        """
        if not len(resource_ids) == 2:
            raise osv.except_osv(_('Error!'), _('You must select only two resources'))
        return True

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(base_product_merge, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
        resource_ids = context.get('active_ids') or []

        self.check_resources_to_merge(cr, uid, resource_ids, context)

        if not len(resource_ids) == 2:
            return res
        obj = self.pool.get('product.product')
        cr.execute("SELECT id, name, field_description, ttype, required, relation, readonly from ir_model_fields where model in ('product.product', 'product.template')")
        field_datas = cr.fetchall()
        obj1 = obj.browse(cr, uid, resource_ids[0], context=context)
        obj2 = obj.browse(cr, uid, resource_ids[1], context=context)
        myxml, merge_fields, self._values, columns = self._build_form(cr, uid, field_datas, obj1, obj2)
        self._columns.update(columns)
        res['arch'] = myxml
        res['fields'] = merge_fields
        return res

    def cast_many2one_fields(self, cr, uid, data_record, context=None):
        """ Some fields are many2one and the ORM expect them to be integer or in the form
        'relation,1' wher id is the id.
         As some fields are displayed as selection in the view, we cast them in integer.
        """
        cr.execute("SELECT name from ir_model_fields where model in ('product.product', 'product.template') and ttype='many2one'")
        fields = cr.fetchall()
        for field in fields:
            if data_record.get(field[0], False):
                data_record[field[0]] = int(data_record[field[0]])
        return data_record

    def action_merge(self, cr, uid, ids, context=None):
        """
        Merges two resources and create 3rd and changes references of old resources with new
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user s ID for security checks,
        @param ids: id of the wizard
        @param context: A standard dictionary for contextual values

        @return : dict to open the new product in a view
        """
        record_id = context and context.get('active_id', False) or False
        pool = self.pool
        if not record_id:
            return {}
        res = self.read(cr, uid, ids, context = context)[0]

        res.update(self._values)
        resource_ids = context.get('active_ids') or []
        
        self.check_resources_to_merge(cr, uid, resource_ids, context)

        resource1 = resource_ids[0]
        resource2 = resource_ids[1]

        obj, obj_parent = pool.get('product.product'), pool.get('product.template')

        remove_field = {}
        # for uniqueness constraint: empty the field in the old resources
        c_names = []
        for check_obj in (obj, obj_parent):
            if hasattr(check_obj, '_sql_constraints'):
                remove_field = {}
                for const in check_obj._sql_constraints:
                    c_names.append(check_obj._name.replace('.', '_') + '_' + const[0])
        if c_names:
            c_names = tuple(map(lambda x: "'"+ x +"'", c_names))
            cr.execute("""select column_name from \
                        information_schema.constraint_column_usage u \
                        join  pg_constraint p on (p.conname=u.constraint_name) \
                        where u.constraint_name in (%s) and p.contype='u' """ % c_names)
            for i in cr.fetchall():
                remove_field[i[0]] = False

        remove_field.update({'active': False})

        obj.write(cr, uid, [resource1, resource2], remove_field, context=context)

        res = self.cast_many2one_fields(cr, uid, res, context)

        res_id = obj.create(cr, uid, res, context=context)

        self.custom_updates(cr, uid, res_id, [resource1, resource2], context)

        # For one2many fields on the resource
        cr.execute("select name, model from ir_model_fields where relation in ('product.product', 'product.template') and ttype not in ('many2many', 'one2many');")
        for name, model_raw in cr.fetchall():
            if hasattr(pool.get(model_raw), '_auto'):
                if not pool.get(model_raw)._auto:
                    continue
            elif hasattr(pool.get(model_raw), '_check_time'):
                continue
            else:
                if hasattr(pool.get(model_raw), '_columns'):
                    from osv import fields
                    if pool.get(model_raw)._columns.get(name, False) and isinstance(pool.get(model_raw)._columns[name], fields.many2one):
                        model = model_raw.replace('.', '_')
                        if name not in self.MERGE_SKIP_FIELDS:
                            cr.execute("update "+model+" set "+name+"="+str(res_id)+" where "+ tools.ustr(name) +" in ("+ tools.ustr(resource1) +", "+tools.ustr(resource2)+")")

        value = {
            'domain': str([('id', '=', res_id)]),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'product.product',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': res_id
        }
        return value

    def custom_updates(self, cr, uid, resource_id, old_resources_ids, context):
        """Hook for special updates on old resources and new resource
        """
        pass

base_product_merge()

