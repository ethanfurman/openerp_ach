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
from fnx.finance import ACHPayment

class res_partner_bank(osv.osv):
    """Bank Accounts"""
    _name = "res.partner.bank"
    _inherit = "res.partner.bank"

    _columns = {
        'ach_default': fields.boolean('Default ACH account', help="Have this account automatically selected for ACH payments?"),

        'ach_bank_name': fields.char('Name', size=23, help="Immediate Destination Name [23]"),
        'ach_bank_number': fields.char('Number', size=9, help="Immediate Destination [9]"),
        'ach_bank_id': fields.char('ID', size=8, help="Originating DFI [8]"),

        'ach_company_name': fields.char('Name', size=23, help="Immediate Origin Name [23]"),
        'ach_company_number': fields.char('Number', size=10, help="Immediate Origin [10]"),
        'ach_company_name_short': fields.char('Name (short)', size=16, help="Company Name [16]"),
        'ach_company_id': fields.char('ID', size=10, help="Company ID [10]"),
    }

    _defaults = {
        'ach_default': lambda obj, cursor, user, context: False,
    }

    def _unset_default_ach(self, cr, uid, ids=None, values=None, context=None):
        if ids is None:
            ids = [0]
        ach_candidate_count = 0
        if values.get('ach_default'):
            ach_candidate_count = len(ids)
        if not ach_candidate_count:
            return
        elif ach_candidate_count > 1:
            raise osv.except_osv("Too many defaults",'Only one account can be set as the default ACH account.')
        records = self.browse(cr, uid, self.search(cr, uid, [('id','not in',ids), ('state','=','ach')], context=context), context=context)
        for rec in records:
            super(res_partner_bank, self).write(cr, uid, rec.id, {'ach_default':False}, context=context)

    def create(self, cr, uid, values, context=None):
        self._unset_default_ach(cr, uid, values=values, context=context)
        return super(res_partner_bank, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        if ids:
            self._unset_default_ach(cr, uid, ids, values, context=context)
        return super(res_partner_bank, self).write(cr, uid, ids, values, context=context)

res_partner_bank()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
