import logging
import werkzeug
from werkzeug.urls import url_encode
from odoo import http, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.home import ensure_db, Home, \
    SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS

_logger = logging.getLogger(__name__)

LOGIN_SUCCESSFUL_PARAMS.add('account_created')


class AuthSignupHome(Home):
    """Portal user login"""

    @http.route()
    def web_login(self, *args, **kw):
        """Function handles login features"""
        response = super().web_login(*args, **kw)
        if response.qcontext and response.qcontext.get('login', False):
            inactive_user = request.env['res.users.approve'].sudo().search(
                [('name', '=', response.qcontext.get('login')),
                 ('for_approval_menu', '=', False)])
            if inactive_user:
                response.qcontext["error"] = _(
                    "You can login only after your login gets approved..!")
        return response

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        """Function handles signup features"""
        qcontext = self.get_auth_signup_qcontext()
        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        signup_approval = request.env['ir.config_parameter'].sudo().get_param(
            'website_signup_approval.auth_signup_approval')

        if values and signup_approval:
            return request.redirect('/success')

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                if qcontext.get('token'):
                    user = request.env['res.users']
                    user_sudo = user.sudo().search(
                        user._get_login_domain(qcontext.get('login')),
                        order=user._get_login_order(), limit=1
                    )
                    template = request.env.ref(
                        'auth_signup.mail_template_user_signup_account_created',
                        raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search(
                        [("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _(
                        "Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")
        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search(
                [('email', '=', qcontext.get('signup_email')),
                 ('state', '!=', 'new')], limit=1)
            if user:
                return request.redirect('/web/login?%s' % url_encode(
                    {'login': user.login, 'redirect': '/web'}))

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    @http.route('/success', type='http', auth='public', website=True, sitemap=False)
    def approval_success(self):
        """Create approval request success form"""
        return request.render("website_signup_approval.approval_form_success")


class SignUpApproveController(http.Controller):
    """Manage Approval Request in Backend"""

    @http.route(['/web/signup/approve'], type='json', auth='public')
    def create_attachment(self, **dat):
        """Create approval request and send notification only when a new request is created"""

        _logger.info("Received Data: %s", dat)

        # Prepare attachments
        data_list = []
        if dat.get('data'):
            for data in dat['data']:
                try:
                    data = data.split('base64')[1] if 'base64' in data else False
                    if data:
                        data_list.append((0, 0, {'attachments': data}))
                except Exception as e:
                    _logger.error("Error processing attachment data: %s", e)

        # Check if the email already exists
        existing_user = request.env['res.users.approve'].sudo().search([('email', '=', dat.get('email'))])
        if existing_user:
            _logger.warning("Email %s already exists. Skipping creation.", dat.get('email'))
            return {'error': 'Email already exists'}

        try:
            # Create new approval request
            attach = request.env['res.users.approve'].sudo().create({
                'name': f"{dat.get('first_name', '')} {dat.get('last_name', '')}".strip(),
                'email': dat.get('email'),
                'password': dat.get('password'),
                'first_name': dat.get('first_name'),
                'last_name': dat.get('last_name'),
                'company_name': dat.get('company_name'),
                'birthday': dat.get('birthday'),
                'street': dat.get('street'),
                'address_supplement': dat.get('address_supplement'),
                'province': dat.get('province'),
                'city': dat.get('city'),
                'postal_code': dat.get('postal_code'),
                'phone': dat.get('phone'),
                'recommended_by': dat.get('recommended_by'),
                'gender': dat.get('gender'),
                'accept_terms': dat.get('accept_terms'),
                'attachment_ids': data_list,
            })

            # Create attachments in ir.attachment
            for data in dat.get('data', []):
                try:
                    data = data.split('base64')[1] if 'base64' in data else False
                    if data:
                        request.env['ir.attachment'].sudo().create({
                            'name': attach.name,
                            'datas': data,
                            'res_model': 'res.users.approve',
                            'res_id': attach.id,
                        })
                except Exception as e:
                    _logger.error("Error creating attachment: %s", e)

            _logger.info("Approval request created successfully for: %s", dat.get('email'))

            # **Send Notification Email Only When a New Approval Request is Created**
            notification_emails = request.env['signup.notification'].sudo().search([]).mapped('email')
            notification_emails_str = ','.join(notification_emails)

            template = request.env.ref(
                'website_signup_approval.mail_template_signup_notification',
                raise_if_not_found=False
            )

            if template and notification_emails_str:
                template.sudo().send_mail(
                    attach.id,
                    email_values={'email_to': notification_emails_str},
                    force_send=True
                )
                _logger.info("Signup notification sent to: %s", notification_emails_str)

            return {'success': 'Record created successfully'}

        except Exception as e:
            _logger.error("Error creating approval request: %s", e)
            return {'error': 'Failed to create approval request. Please check logs.'}
