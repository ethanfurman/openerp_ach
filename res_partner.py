from fnx import all_equal, ACHPayment
from openerp.osv import fields, osv

class res_partner(osv.Model):
    _inherit = "res.partner"
    _columns = {
            'ach_type': fields.selection([('domestic', 'Domestic'), ('foreign', 'Foreign')], "Type of account"),
            'ach_routing': fields.char('ACH Routing #', size=9, help="Partner's bank's routing number"),
            'ach_account': fields.char('ACH Account #', size=32, help="Partner's account at bank."),
            }

    def _validate_ach(self, values, record=None):
        if record is None:
            existing = {}
        else:
            existing = dict(ach_type=record.ach_type, ach_routing=record.ach_routing, ach_account=record.ach_account)
        proposed = {}
        proposed['ach_type'] = values.get('ach_type')
        proposed['ach_routing'] = values.get('ach_routing')
        proposed['ach_account'] = values.get('ach_account')
        proposed.update(existing)
        # either all three have values, or all three are empty
        values = proposed.values()
        if not (all_equal(values, lambda v: bool(v) is False) or all_equal(values, lambda v: bool(v) is True)):
            raise osv.except_osv('Information Missing', 'Either all the ACH fields must be filled out, or none of them')
        route = proposed.get('ach_routing')
        if route:
            ACHPayment.validate_routing(route)
        if proposed.get('ach_type') == 'foreign':
            raise osv.except_osv('Not Implemented', 'Foreign ACH is not yet implemented.')
        return True

    def create(self, cr, uid, values, context=None):
        self._validate_ach(values)
        return super(res_partner, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        if len(ids) <= 2:
            if ids:
                record = self.browse(cr, uid, ids[0], context=context)
            else:
                record = None
            self._validate_ach(values)
        else:
            for id, new_values in values.items():
                record = self.browse(cr, uid, id, context=context)
                self._validate_ach(new_values, record)
        return super(res_partner, self).write(cr, uid, ids, values, context=context)

res_partner()
