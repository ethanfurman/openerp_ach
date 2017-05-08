from automated_clearing_house.ach import ach
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID

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

    fields.apply_groups(
            _columns,
            {'automated_clearing_house.configure,automated_clearing_house.setup,automated_clearing_house.approve':
                ['ach_.*']},
            )

    def ach_users(self, cr, uid, context=None):
        ach_users = []
        for user in  self.pool.get('res.users').browse(cr, SUPERUSER_ID, context=context):
            for group in user.groups_id:
                if group.full_name in (
                        'Automated Clearing House / Configure Partner Info',
                        'Automated Clearing House / Approve Partner Info',
                        ):
                    ach_users.append(user)
                    break
        return ach_users
