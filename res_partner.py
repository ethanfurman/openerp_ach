from fnx import validate_ach
from openerp.osv import fields, osv

class res_partner(osv.Model):
    _inherit = "res.partner"
    _columns = {
        'ach_type': fields.selection([('domestic', 'Domestic'), ('foreign', 'Foreign')], "Type of account"),
        'ach_routing': fields.char('ACH Routing #', size=9, help="Partner's bank's routing number"),
        'ach_account': fields.char('ACH Account #', size=32, help="Partner's account at bank."),
        'ach_verified': fields.selection([('unverified','Not Verified'), ('testing','Testing'), ('verified','Verified'), ('inactive','Verified (inactive)')], 'ACH Status'),
        'ach_amount': fields.integer('Ach Amount'),
        'ach_date': fields.date('Last Transaction'),
        }

    def create(self, cr, uid, values, context=None):
        validate_ach(values)
        return super(res_partner, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        if ids:
            if isinstance(ids, (int, long)):
                ids = [ids]
            for partner in self.browse(cr, uid, id, context=context):
                validate_ach(values, partner)
        return super(res_partner, self).write(cr, uid, ids, values, context=context)

res_partner()
