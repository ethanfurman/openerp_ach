from fnx import all_equal
from fnx.finance import ACHPayment
from openerp.osv import fields, osv

class res_partner(osv.Model):
    _inherit = "res.partner"
    _columns = {
        'ach_type': fields.selection([('domestic', 'Domestic'), ('foreign', 'Foreign')], "Type of account"),
        'ach_routing': fields.char('ACH Routing #', size=9, help="Partner's bank's routing number"),
        'ach_account': fields.char('ACH Account #', size=32, help="Partner's account at bank."),
        'ach_verified': fields.selection([('unverified','Not Verified'), ('testing','Testing'), ('verified','Verified')], 'ACH Status'),
        'ach_amount': fields.integer('Ach Amount'),
        'ach_date': fields.date('Last Transaction'),
        }

    def _validate_ach(self, values, record=None):
        if record is None:
            record = PropertyDict(ach_type=False, ach_routing=False, ach_account=False)
        proposed = {}
        proposed['ach_type'] = values.get('ach_type', record.ach_type)
        proposed['ach_routing'] = values.get('ach_routing', record.ach_routing)
        proposed['ach_account'] = values.get('ach_account', record.ach_account)
        # either all three have values, or all three are empty
        proposed_values = proposed.values()
        if all_equal(proposed_values, lambda v: bool(v) is False):
            action = 'clear'
        elif all_equal(proposed_values, lambda v: bool(v) is True):
            action = 'set'
        else:
            raise osv.except_osv('Information Missing', 'Either all the ACH fields must be filled out, or none of them')
        if action == 'clear':
            values['ach_verified'] = False
            values['ach_amount'] = False
            values['ach_date'] = False
        elif action == 'set':
            if proposed.get('ach_type') == 'foreign':
                raise osv.except_osv('Not Implemented', 'Foreign ACH is not yet implemented.')
            route = proposed['ach_routing']
            try:
                ACHPayment.validate_routing(route)
            except ValueError:
                raise osv.except_osv('Invalid', 'Routing number %s fails check digit calculation' % route)
            if 'ach_account' in values or 'ach_routing' in values:
                values['ach_verified'] = 'unverified'
                values['ach_amount'] = 0
        return True

    def create(self, cr, uid, values, context=None):
        self._validate_ach(values)
        return super(res_partner, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        if ids:
            if isinstance(ids, (int, long)):
                ids = [ids]
            for id in ids:
                record = self.browse(cr, uid, id, context=context)
                self._validate_ach(values, record)
        return super(res_partner, self).write(cr, uid, ids, values, context=context)

res_partner()
