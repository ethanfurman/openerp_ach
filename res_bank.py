# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _

class Bank(osv.osv):
    """Banks"""
    _name = 'res.bank'
    _inherit = 'res.bank'

    _columns = {
        'ach_name': fields.char('ACH Name', size=23, help="Name to use for ACH transactions"),
        'ach_routing': fields.char('ACH Routing Number', size=8, help="Routing number to use for ACH transactions"),
    }
Bank()


class res_partner_bank(osv.osv):
    """Bank Accounts"""
    _name = "res.partner.bank"
    _inherit = "res.partner.bank"

    _columns = {
        'ach_default': fields.boolean('Default ACH account', help="Have this account automatically selected for ACH payments?"),
        'ach_bank_name': fields.char('ACH Name', size=23, help="Name to use for ACH transactions"),
        'ach_bank_routing': fields.char('ACH Routing Number', size=8, help="Routing number to use for ACH transactions"),
    }

    _defaults = {
        'ach_default': lambda obj, cursor, user, context: False,
    }

    @staticmethod
    def _check_bank_id(values, record=None):
        proposed = {}
        if record:
            proposed.update(record)
        proposed.update(values)
        if proposed.get('state') != 'ach':
            return
        bank_id = proposed.get('bank_bic')
        if bank_id is None or len(bank_id) > 8:
            raise osv.except_osv('Invalid Data', 'The Bank Indentifier Code for ACH accounts must be no more that 8 digits long\n%r' % bank_id)

    def _unset_default_ach(self, cr, uid, ids=None, values=None, context=None):
        if ids is None:
            ids = [0]
        if len(ids) == 1:
            new_values = {}
            new_values[ids[0]] = values
        else:
            new_values = values
        ach_candidate_count = 0
        for id, values in new_values.items():
            if values.get('ach_default'):
                ach_candidate_count += 1
        if not ach_candidate_count:
            return
        elif ach_candidate_count > 1:
            raise osv.except_osv("Too many defaults",'Only one account can be set as the default ACH account.')
        records = self.browse(cr, uid, self.search(cr, uid, [('id','not in',ids), ('state','=','ach')], context=context), context=context)
        for rec in records:
            super(res_partner_bank, self).write(cr, uid, rec.id, {'ach_default':False}, context=context)

    def onchange_bank_id(self, cr, uid, ids, bank_id, context=None):
        result = {}
        if bank_id:
            result = super(res_partner_bank, self).onchange_bank_id(cr, uid, ids, bank_id, context=context)
            bank = self.pool.get('res.bank').browse(cr, uid, bank_id, context=context)
            result['value']['ach_bank_name'] = bank.ach_name
            result['value']['ach_bank_routing'] = bank.ach_routing
        return result

    def create(self, cr, uid, values, context=None):
        self._check_bank_id(values)
        return super(res_partner_bank, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        if ids:
            self._unset_default_ach(cr, uid, ids, values, context=context)
        return super(res_partner_bank, self).write(cr, uid, ids, values, context=context)

res_partner_bank()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
