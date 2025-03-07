# import logging
# import werkzeug
# from werkzeug.urls import url_encode
# from odoo import http, _
# from odoo.exceptions import UserError
# from odoo.http import request
# from odoo.addons.auth_signup.models.res_users import SignupError
# from odoo.addons.web.controllers.home import ensure_db, Home, \
#     SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS
#
# _logger = logging.getLogger(__name__)
#
#
# LOGIN_SUCCESSFUL_PARAMS.add('account_created')

#
# class AuthSignupHome(Home):
#     """Portal user login"""
#     @http.route()
#     def web_login(self, *args, **kw):
#         """Function have login features"""
#         response = super().web_login(*args, **kw)
#         if response.qcontext and response.qcontext.get('login', False):
#             inactive_user = request.env['res.users.approve'].sudo().search(
#                 [('name', '=', response.qcontext.get('login')),
#                  ('for_approval_menu', '=', False)])
#             if inactive_user:
#                 response.qcontext["error"] = _(
#                     "You can login only after your login get approved..!")
#         return response
#
#
#     @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
#     def web_auth_signup(self, *args, **kw):
#         """Function have signup features"""
#         qcontext = self.get_auth_signup_qcontext()
#         values = {k: v for k, v in request.params.items() if
#                   k in SIGN_UP_REQUEST_PARAMS}
#         signup_approval = request.env['ir.config_parameter'].sudo().get_param(
#             'website_signup_approval.auth_signup_approval')
#         if values:
#             if signup_approval:
#                 return request.redirect('/success')
#         if not qcontext.get('token') and not qcontext.get('signup_enabled'):
#             raise werkzeug.exceptions.NotFound()
#         if 'error' not in qcontext and request.httprequest.method == 'POST':
#             try:
#                 self.do_signup(qcontext)
#                 if qcontext.get('token'):
#                     user = request.env['res.users']
#                     user_sudo = user.sudo().search(
#                         user._get_login_domain(qcontext.get('login')),
#                         order=user._get_login_order(), limit=1
#                     )
#                     template = request.env.ref(
#                         'auth_signup.mail_template_user_signup_account_created',
#                         raise_if_not_found=False)
#                     if user_sudo and template:
#                         template.sudo().send_mail(user_sudo.id,
#                                                   force_send=True)
#                 return self.web_login(*args, **kw)
#             except UserError as e:
#                 qcontext['error'] = e.args[0]
#             except (SignupError, AssertionError) as e:
#                 if request.env["res.users"].sudo().search(
#                         [("login", "=", qcontext.get("login"))]):
#                     qcontext["error"] = _(
#                         "Another user is already registered using this email "
#                         "address.")
#                 else:
#                     _logger.error("%s", e)
#                     qcontext['error'] = _("Could not create a new account.")
#         elif 'signup_email' in qcontext:
#             user = request.env['res.users'].sudo().search(
#                 [('email', '=', qcontext.get('signup_email')),
#                  ('state', '!=', 'new')], limit=1)
#             if user:
#                 return request.redirect('/web/login?%s' % url_encode(
#                     {'login': user.login, 'redirect': '/web'}))
#         response = request.render('auth_signup.signup', qcontext)
#         response.headers['X-Frame-Options'] = 'SAMEORIGIN'
#         response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
#
#         # Fetch email from system parameters
#         notification_emails = request.env['signup.notification'].sudo().search([]).mapped('email')
#
#         # Ensure notification_emails is a comma-separated string
#         notification_emails_str = ','.join(notification_emails)
#
#         template = request.env.ref(
#             'website_signup_approval.mail_template_signup_notification',
#             raise_if_not_found=False
#         )
#
#         if template and notification_emails_str:
#             template.sudo().send_mail(
#                 request.env.user.id,
#                 email_values={'email_to': notification_emails_str},
#                 force_send=True
#             )
#
#
#         # notification_email = request.env['ir.config_parameter'].sudo().get_param(
#         #     'website_signup_notification.email', default='rapidgrps@gmail.com'
#         # )
#         #
#         # # notification_emails = request.env['signup.notification'].sudo().search([]).mapped('email')
#         # # for email in notification_emails:
#         # #     if email:
#         # #         template.sudo().send_mail(
#         # #             request.env.user.id,
#         # #             email_values={'email_to': email},
#         # #             force_send=True
#         # #         )
#         #
#         # template = request.env.ref('website_signup_approval.mail_template_signup_notification',
#         #                            raise_if_not_found=False)
#         # if template and notification_email:
#         #     template.sudo().send_mail(
#         #         request.env.user.id,
#         #         email_values={'email_to': notification_email},
#         #         force_send=True
#         #     )
#         # Fetch email from system parameters
#
#         return response

    #
    # @http.route('/success', type='http', auth='public', website=True,
    #             sitemap=False)
    # def approval_success(self):
    #     """Create approval request success form"""
    #     return request.render("website_signup_approval.approval_form_success")

#
# class SignUpApproveController(http.Controller):
#     """Manage Approval Request in Backend"""
#
#     @http.route(['/web/signup/approve'], type='json', auth='public')
#     def create_attachment(self, **dat):
#         """Create approval request and attachment in backend"""
#
#         # Debugging: Log the incoming data
#         _logger.info("Received Data: %s", dat)
#
#         # Prepare the attachments list
#         data_list = []
#         if dat.get('data'):  # Ensure 'data' exists to avoid errors
#             for data in dat['data']:
#                 try:
#                     data = data.split('base64')[1] if 'base64' in data else False
#                     if data:
#                         data_list.append((0, 0, {'attachments': data}))
#                 except Exception as e:
#                     _logger.error("Error processing attachment data: %s", e)
#
#         # Check if the email already exists
#         existing_user = request.env['res.users.approve'].sudo().search([('email', '=', dat.get('email'))])
#         if existing_user:
#             _logger.warning("Email %s already exists. Skipping creation.", dat.get('email'))
#             return {'error': 'Email already exists'}
#
#         try:
#             # Create the record in 'res.users.approve'
#             attach = request.env['res.users.approve'].sudo().create({
#                 'name': f"{dat.get('first_name', '')} {dat.get('last_name', '')}".strip(),
#                 'email': dat.get('email'),
#                 'password': dat.get('password'),
#                 'first_name': dat.get('first_name'),
#                 'last_name': dat.get('last_name'),
#                 'company_name': dat.get('company_name'),
#                 'birthday': dat.get('birthday'),
#                 'street': dat.get('street'),
#                 'address_supplement': dat.get('address_supplement'),
#                 'province': dat.get('province'),
#                 'city': dat.get('city'),
#                 'postal_code': dat.get('postal_code'),
#                 'phone': dat.get('phone'),
#                 'recommended_by': dat.get('recommended_by'),
#                 'gender': dat.get('gender'),
#                 'accept_terms': dat.get('accept_terms'),
#                 'attachment_ids': data_list,
#             })
#
#             # Create ir.attachments related to the new record
#             for data in dat.get('data', []):
#                 try:
#                     data = data.split('base64')[1] if 'base64' in data else False
#                     if data:
#                         request.env['ir.attachment'].sudo().create({
#                             'name': attach.name,
#                             'datas': data,
#                             'res_model': 'res.users.approve',
#                             'res_id': attach.id,
#                         })
#                 except Exception as e:
#                     _logger.error("Error creating attachment: %s", e)
#
#             _logger.info("Approval request created successfully for: %s", dat.get('email'))
#             return {'success': 'Record created successfully'}
#
#         except Exception as e:
#             _logger.error("Error creating approval request: %s", e)
#             return {'error': 'Failed to create approval request. Please check logs.'}

#
# from odoo import http, _
# from odoo.http import request
# from odoo.addons.auth_signup.controllers.main import AuthSignupHome
# from odoo.exceptions import UserError
#
# class CustomAuthSignupHome(AuthSignupHome):
#
#     @http.route('/web/reset_password', type='http', auth='public', website=True, csrf=False)
#     def web_auth_reset_password(self, *args, **kw):
#         qcontext = self.get_auth_signup_qcontext()
#
#         # Password Reset via Token
#         if 'token' in qcontext and not qcontext.get('invalid_token'):
#             if request.httprequest.method == 'POST':
#                 password = kw.get('password')
#                 confirm_password = kw.get('confirm_password')
#
#                 if not password or not confirm_password:
#                     qcontext['error'] = _("Password fields cannot be empty.")
#                     return request.render('auth_signup.reset_password', qcontext)
#
#                 if password != confirm_password:
#                     qcontext['error'] = _("Passwords do not match.")
#                     return request.render('auth_signup.reset_password', qcontext)
#
#                 user = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))], limit=1)
#                 if user:
#                     user.sudo().write({'password': password})
#                     return request.redirect('/web/login')
#                 else:
#                     qcontext['error'] = _("Invalid user.")
#
#         # Request Reset (Email Submission)
#         if request.httprequest.method == 'POST' and not qcontext.get('token'):
#             login = kw.get('login')
#             user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
#             if user:
#                 try:
#                     user.sudo().signup_send_password_reset_email()
#                     qcontext['message'] = _("A password reset link has been sent to your email.")
#                 except Exception as e:
#                     qcontext['error'] = _("Error sending email: ") + str(e)
#             else:
#                 qcontext['error'] = _("User not found.")
#
#         return request.render('auth_signup.reset_password', qcontext)


import logging
import werkzeug
from werkzeug.urls import url_encode
from odoo import http, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.home import ensure_db, Home, SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS

_logger = logging.getLogger(__name__)

LOGIN_SUCCESSFUL_PARAMS.add('account_created')

class AuthSignupHome(Home):
    @http.route()
    def web_login(self, *args, **kw):
        response = super().web_login(*args, **kw)
        if response.qcontext and response.qcontext.get('login', False):
            inactive_user = request.env['res.users.approve'].sudo().search(
                [('name', '=', response.qcontext.get('login')), ('for_approval_menu', '=', False)]
            )
            if inactive_user:
                response.qcontext["error"] = _("You can login only after your login is approved.")
        return response

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        signup_approval = request.env['ir.config_parameter'].sudo().get_param('website_signup_approval.auth_signup_approval')

        if values and signup_approval:
            return request.redirect('/success')

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                if qcontext.get('token'):
                    user = request.env['res.users']
                    user_sudo = user.sudo().search(user._get_login_domain(qcontext.get('login')),
                                                   order=user._get_login_order(), limit=1)
                    if user_sudo:
                        account_created_template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                                                    raise_if_not_found=False)
                        if account_created_template:
                            account_created_template.sudo().send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("Signup error: %s", e)
                    qcontext['error'] = _("Could not create a new account.")
        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search([('email', '=', qcontext.get('signup_email')), ('state', '!=', 'new')], limit=1)
            if user:
                return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"

        # Handle signup notification emails
        if not request.env['ir.config_parameter'].sudo().get_param('disable_signup_notifications'):
            notification_emails = request.env['signup.notification'].sudo().search([]).mapped('email')
            if notification_emails:
                notification_emails_str = ','.join(notification_emails)
                signup_notification_template = request.env.ref('website_signup_approval.mail_template_signup_notification',
                                                               raise_if_not_found=False)
                if signup_notification_template:
                    signup_notification_template.sudo().send_mail(
                        request.env.user.id,
                        email_values={'email_to': notification_emails_str},
                        force_send=True
                    )
        else:
            _logger.info("Signup notifications are disabled.")

        return response

    @http.route('/success', type='http', auth='public', website=True, sitemap=False)
    def approval_success(self):
        return request.render("website_signup_approval.approval_form_success")


class SignUpApproveController(http.Controller):
    """Manage Approval Request in Backend"""

    @http.route(['/web/signup/approve'], type='json', auth='public')
    def create_attachment(self, **dat):
        """Create approval request and attachment in backend"""

        _logger.info("Received Data: %s", dat)

        data_list = []
        if dat.get('data'):
            for data in dat['data']:
                try:
                    data = data.split('base64')[1] if 'base64' in data else False
                    if data:
                        data_list.append((0, 0, {'attachments': data}))
                except Exception as e:
                    _logger.error("Error processing attachment data: %s", e)

        existing_user = request.env['res.users.approve'].sudo().search([('email', '=', dat.get('email'))])
        if existing_user:
            _logger.warning("Email %s already exists. Skipping creation.", dat.get('email'))
            return {'error': 'Email already exists'}

        try:
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
            return {'success': 'Record created successfully'}

        except Exception as e:
            _logger.error("Error creating approval request: %s", e)
            return {'error': 'Failed to create approval request. Please check logs.'}
