from fnx import Date, PropertyDict, all_equal, finance
from osv.osv import except_osv as ERPError

def validate_ach(values, record=None):
    if not any([k[:4] == 'ach_' for k in values]):
        # if no ach changes, no need to continue
        return True
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
        raise ERPError('Information Missing', 'Either all the ACH fields must be filled out, or none of them')
    if action == 'clear':
        values['ach_verified'] = False
        values['ach_amount'] = False
        values['ach_date'] = False
    elif action == 'set':
        if proposed.get('ach_type') == 'foreign':
            raise ERPError('Not Implemented', 'Foreign ACH is not yet implemented.')
        route = proposed['ach_routing']
        try:
            finance.ACHPayment.validate_routing(route)
        except ValueError:
            raise ERPError('Invalid', 'Routing number %s fails check digit calculation' % route)
        if 'ach_account' in values or 'ach_routing' in values:
            values['ach_verified'] = 'unverified'
            values['ach_amount'] = 0
            values['ach_date'] = False
    return True


class ach(object):
    # fields that should be in inheriting table:
    # ach_[type, routing, account, verified, amount, date]

    def create(self, cr, uid, values, context=None):
        validate_ach(values)
        return super(ach, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        if ids:
            if isinstance(ids, (int, long)):
                ids = [ids]
            for partner in self.browse(cr, uid, ids, context=context):
                validate_ach(values, partner)
        return super(ach, self).write(cr, uid, ids, values, context=context)

