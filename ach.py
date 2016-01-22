from fnx import Date, DateTime, PropertyDict, all_equal, finance, mail
from osv.osv import except_osv as ERPError
from openerp import SUPERUSER_ID as SUPERUSER
import logging

_logger = logging.getLogger(__name__)


class ach(object):
    # fields that should be in inheriting table:
    # ach_[type, routing, account, verified, amount, date]

    def create(self, cr, uid, values, context=None):
        new_id = super(ach, self).create(cr, uid, values, context=context)
        ctx = context and context.copy() or {}
        ctx['ach'] = 'create'
        self.validate_ach(cr, uid, [new_id], values, context=ctx)
        return new_id

    def validate_ach(self, cr, uid, ids, values, context=None):
        if context is None:
            context = {}
        if not any([k[:4] == 'ach_' for k in values]):
            # if no ach changes, no need to continue
            return True
        if isinstance(ids, (int, long)):
            ids = [ids]
        # get info needed for email
        # - mail server to use from ir.mail_server, lowest numbered 'sequence'
        # - users to mail: all users with the appropriate 'configure' or 'approve' permissions
        # mail_server = min(self.pool.get('ir.mail_server').browse(cr, SUPERUSER), key=lambda ms: ms.sequence)
        # smtp_host = {'192.168.33.240':'westernstatesglass.com'}.get(mail_server.smtp_host, mail_server.smtp_host)
        # mail_headers = ['From: OpenERP <noreply@%s>' % smtp_host]
        mail_headers = []
        for user in self.ach_users(cr, uid, context=context):
            if user.email:
                mail_headers.append('To: %s <%s>' % (user.name, user.email))
            else:
                _logger.warn('%s does not have an email address', user.name)
        for entity in self.browse(cr, uid, ids, context=context):
            mail_subject = None
            entity_name = values.get('name') or entity.name
            proposed = {
                    'ach_type'    : values.get('ach_type', entity.ach_type),
                    'ach_routing' : values.get('ach_routing', entity.ach_routing),
                    'ach_account' : values.get('ach_account', entity.ach_account),
                    }
            # either all three have values, or all three are empty
            if all_equal(proposed.values(), lambda v: bool(v) is True):
                action = 'set'
            elif all_equal(proposed.values(), lambda v: bool(v) is False):
                action = 'clear'
                # if this was a brand new record, no need to send email
                if context.get('ach') == 'create':
                    continue
            else:
                raise ERPError('Information Missing', 'Either all the ACH fields must be filled out, or none of them')
            if action == 'clear':
                values['ach_verified'] = False
                values['ach_amount'] = False
                values['ach_date'] = Date.today()
                mail_subject = 'ACH data removed from: %s' % entity_name
            elif action == 'set':
                if proposed.get('ach_type') == 'foreign':
                    raise ERPError('Not Implemented', 'Foreign ACH is not yet implemented.')
                route = proposed['ach_routing']
                try:
                    finance.ACHPayment.validate_routing(route)
                except ValueError:
                    raise ERPError('Invalid', 'Routing number %s fails check digit calculation' % route)
                if 'ach_account' in values or 'ach_routing' in values:
                    # bank info changing
                    values['ach_verified'] = 'unverified'
                    values['ach_amount'] = 0
                    values['ach_date'] = Date.today()
                    mail_subject = 'ACH data changed for: %s' % entity_name
                elif 'ach_verified' in values:
                    # verification status changing
                    values['ach_date'] = Date.today()
                    mail_subject = 'ACH status changed for: %s' % entity_name
            if mail_subject is not None:
                mail_headers = '\n'.join(mail_headers) + '\nSubject: ' + mail_subject + '\n\n'
                mail_body = 'name: %(name)s\nby:   %(user)s\nat:   %(date)s\nfrom: %(ip)s'
                if 'ach_verified' in values:
                    if entity.ach_verified == values['ach_verified']:
                        # same value means a created record
                        mail_body += '\nstatus: %(new_status)s'
                    else:
                        # values are different, record both
                        mail_body += '\nold status: %(old_status)s\nnew status: %(new_status)s'
                mail_values = {
                        'ip':   context.get('__client_address__', 'unknown'),
                        'date': DateTime.now(),
                        'name': entity_name,
                        'user': self.pool.get('res.users').browse(cr, uid, [('id','=',uid)])[0].name,
                        'old_status': entity.ach_verified,
                        'new_status': values.get('ach_verified', 'None')
                        }
                mail_message = mail_headers + mail_body % mail_values
                mail(self, cr, uid, mail_message)
        return True

    def write(self, cr, uid, ids, values, context=None):
        if ids:
            self.validate_ach(cr, uid, ids, values, context=context)
        return super(ach, self).write(cr, uid, ids, values, context=context)
