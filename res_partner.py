from automated_clearing_house.ach import ach
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID as SUPERUSER

class res_partner(ach, osv.Model):
    _name = 'res.partner'
    _inherit = "res.partner"

    _columns = {
        'ach_type': fields.selection([('domestic', 'Domestic'), ('foreign', 'Foreign')], "Type of account"),
        'ach_routing': fields.char('ACH Routing #', size=9, help="Partner's bank's routing number"),
        'ach_account': fields.char('ACH Account #', size=32, help="Partner's account at bank."),
        'ach_verified': fields.selection([('unverified','Not Verified'), ('testing','Testing'), ('verified','Verified'), ('inactive','Verified (inactive)')], 'ACH Status'),
        'ach_amount': fields.integer('Ach Amount'),
        'ach_date': fields.date('Last Transaction'),
        }

    def ach_users(self, cr, uid, context=None):
        return self.pool.get('res.users').browse(cr, SUPERUSER, [
            '|',
            ('groups_id.full_name','=','Automated Clearing House / Configure Partner Info'),
            ('groups_id.full_name','=','Automated Clearing House / Approve Partner Info'),
            ], context=context)
