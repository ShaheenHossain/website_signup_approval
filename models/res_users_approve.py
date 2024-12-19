from email.policy import default

from odoo import fields, models


class ResUsersApprove(models.Model):
    """Store Signup Information of Users from Website"""
    _name = 'res.users.approve'
    _description = "Approval Request Details"

    # name = fields.Char(help="Name of the user", string='Name')

    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    name = fields.Char(string='Full Name', compute='_compute_full_name', store=True)

    email = fields.Char(help="Email of the user", string="Email")
    password = fields.Char(help="Password of the user", string="Password")

    gender = fields.Selection([
        ('female', 'Female'),
        ('male', 'Male'),
        ('other', 'Other')
    ], string='Gender', default='male')

    birthday = fields.Date(string='Birthday')
    street = fields.Char(string='Street and House Number')
    city = fields.Char(string='City')
    postal_code = fields.Char(string='Postal Code')
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        default=lambda self: self.env.ref('base.ch'))

    phone = fields.Char(string='Phone Number')
    recommended_by = fields.Char(string='Recommended By')
    accept_terms = fields.Boolean(string='Accept Terms and Conditions')

    for_approval_menu = fields.Boolean(string='For Approval Menu',
                                       default=False,
                                       help="Check the request is approved")
    approved_date = fields.Datetime(string='Approved Date', copy=False,
                                    help="Approval date of signup request")
    attachment_ids = fields.One2many('user.approval.window',
                                     'approval_id',
                                     string='Attachments',
                                     help="Store uploaded document")
    hide_button = fields.Boolean(string='For hide button',
                                 default=False,
                                 help="Check the button is used or not")


    def _compute_full_name(self):
        for rec in self:
            rec.name = f"{rec.first_name or ''} {rec.last_name or ''}".strip()

    # def action_approve_login(self):
    #     """To approve the request from website and generate invoice"""
    #     self.for_approval_menu = True
    #     self.hide_button = True
    #
    #     # Approve User Login
    #     user = self.env['res.users'].sudo().search([('login', '=', self.email)])
    #     if not user:
    #         user = self.env['res.users'].sudo().create({
    #             'login': self.email,
    #             'name': self.name,
    #             'password': self.password,
    #             'groups_id': [(4, self.env.ref('base.group_portal').id)]
    #         })
    #         template = self.env.ref(
    #             'auth_signup.mail_template_user_signup_account_created',
    #             raise_if_not_found=False)
    #         email_values = {'email_to': user.login}
    #         template.send_mail(user.id, email_values=email_values, force_send=True)
    #
    #     # Define Service Products
    #     product_joining_fee = self.env['product.product'].search([('name', '=', 'Joining Fee')], limit=1)
    #     product_service_charge = self.env['product.product'].search([('name', '=', 'Service Charge')], limit=1)
    #     product_membership_fee = self.env['product.product'].search([('name', '=', '12 Month Membership Fee')], limit=1)
    #
    #     # Debugging Logs
    #     if not product_joining_fee:
    #         _logger.error("Product 'Joining Fee' is not defined in the database.")
    #     if not product_service_charge:
    #         _logger.error("Product 'Service Charge' is not defined in the database.")
    #     if not product_membership_fee:
    #         _logger.error("Product '12 Month Membership Fee' is not defined in the database.")
    #
    #     if not product_joining_fee or not product_service_charge or not product_membership_fee:
    #         raise ValueError("One or more required service products are not defined. Please ensure all products exist.")
    #
    #     # Create Invoice
    #     invoice_vals = {
    #         'move_type': 'out_invoice',  # Customer Invoice
    #         'partner_id': user.partner_id.id,
    #         'invoice_date': fields.Date.today(),
    #         'invoice_line_ids': [
    #             (0, 0, {
    #                 'product_id': product_joining_fee.id,
    #                 'quantity': 1,
    #                 'price_unit': 25.0,
    #             }),
    #             (0, 0, {
    #                 'product_id': product_service_charge.id,
    #                 'quantity': 1,
    #                 'price_unit': 175.0,
    #             }),
    #             (0, 0, {
    #                 'product_id': product_membership_fee.id,
    #                 'quantity': 1,
    #                 'price_unit': 300.0,
    #             }),
    #         ],
    #     }
    #     invoice = self.env['account.move'].sudo().create(invoice_vals)
    #
    #     # Send Invoice via Email
    #     invoice.sudo().action_post()  # Post the invoice
    #     template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
    #     if template:
    #         template.sudo().send_mail(invoice.id, force_send=True)
    #
    #     return {'message': 'User approved, invoice created and sent successfully.'}

    # def action_approve_login(self):
    #     """To approve the request from website and generate invoice"""
    #     self.for_approval_menu = True
    #     self.hide_button = True
    #
    #     # Approve User Login
    #     user = self.env['res.users'].sudo().search([('login', '=', self.email)])
    #     if not user:
    #         user = self.env['res.users'].sudo().create({
    #             'login': self.email,
    #             'name': self.name,
    #             'password': self.password,
    #             'groups_id': [(4, self.env.ref('base.group_portal').id)]
    #         })
    #         template = self.env.ref(
    #             'auth_signup.mail_template_user_signup_account_created',
    #             raise_if_not_found=False)
    #         email_values = {'email_to': user.login}
    #         template.send_mail(user.id, email_values=email_values, force_send=True)
    #
    #     # Define Service Products
    #     product_joining_fee = self.env['product.product'].search([('name', '=', 'Joining Fee')], limit=1)
    #     product_service_charge = self.env['product.product'].search([('name', '=', 'Service Charge')], limit=1)
    #     product_membership_fee = self.env['product.product'].search([('name', '=', '12 Month Membership Fee')], limit=1)
    #
    #     # Debugging Logs
    #     if not product_joining_fee:
    #         _logger.error("Product 'Joining Fee' is not defined in the database.")
    #     if not product_service_charge:
    #         _logger.error("Product 'Service Charge' is not defined in the database.")
    #     if not product_membership_fee:
    #         _logger.error("Product '12 Month Membership Fee' is not defined in the database.")
    #
    #     if not product_joining_fee or not product_service_charge or not product_membership_fee:
    #         raise ValueError("One or more required service products are not defined. Please ensure all products exist.")
    #
    #     # Create Invoice
    #     invoice_vals = {
    #         'move_type': 'out_invoice',  # Customer Invoice
    #         'partner_id': user.partner_id.id,
    #         'invoice_date': fields.Date.today(),
    #         'invoice_line_ids': [
    #             (0, 0, {
    #                 'product_id': product_joining_fee.id,
    #                 'quantity': 1,
    #                 'price_unit': 25.0,
    #             }),
    #             (0, 0, {
    #                 'product_id': product_service_charge.id,
    #                 'quantity': 1,
    #                 'price_unit': 175.0,
    #             }),
    #             (0, 0, {
    #                 'product_id': product_membership_fee.id,
    #                 'quantity': 1,
    #                 'price_unit': 300.0,
    #             }),
    #         ],
    #     }
    #     invoice = self.env['account.move'].sudo().create(invoice_vals)
    #
    #     # Send Invoice via Email
    #     invoice.sudo().action_post()  # Post the invoice
    #     template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
    #     if template:
    #         template.sudo().send_mail(invoice.id, force_send=True)
    #
    #     # Redirect to Invoice Form View
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Invoice',
    #         'res_model': 'account.move',
    #         'view_mode': 'form',
    #         'res_id': invoice.id,
    #         'target': 'current',
    #     }

    def action_approve_login(self):
        """To approve the request from website and generate invoice"""
        self.for_approval_menu = True
        self.hide_button = True

        # Approve User Login
        user = self.env['res.users'].sudo().search([('login', '=', self.email)])
        if not user:
            user = self.env['res.users'].sudo().create({
                'login': self.email,
                'name': self.name,
                'password': self.password,
                'groups_id': [(4, self.env.ref('base.group_portal').id)],
            })

            # Update associated partner with email and phone
            partner = user.partner_id
            partner.sudo().write({
                'email': self.email,
                'phone': self.phone,
                'street': self.street,
                'city': self.city,
                'zip': self.postal_code,
                'country_id': self.country_id.id,
            })

            # Send notification email to the new user
            template = self.env.ref(
                'auth_signup.mail_template_user_signup_account_created',
                raise_if_not_found=False)
            email_values = {'email_to': user.login}
            template.send_mail(user.id, email_values=email_values, force_send=True)

        # Define Service Products
        product_joining_fee = self.env['product.product'].search([('name', '=', 'Joining Fee')], limit=1)
        product_service_charge = self.env['product.product'].search([('name', '=', 'Service Charge')], limit=1)
        product_membership_fee = self.env['product.product'].search([('name', '=', '12 Month Membership Fee')], limit=1)

        # Debugging Logs
        if not product_joining_fee:
            _logger.error("Product 'Joining Fee' is not defined in the database.")
        if not product_service_charge:
            _logger.error("Product 'Service Charge' is not defined in the database.")
        if not product_membership_fee:
            _logger.error("Product '12 Month Membership Fee' is not defined in the database.")

        if not product_joining_fee or not product_service_charge or not product_membership_fee:
            raise ValueError("One or more required service products are not defined. Please ensure all products exist.")

        # Create Invoice
        invoice_vals = {
            'move_type': 'out_invoice',  # Customer Invoice
            'partner_id': user.partner_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': product_joining_fee.id,
                    'quantity': 1,
                    'price_unit': 25.0,
                }),
                (0, 0, {
                    'product_id': product_service_charge.id,
                    'quantity': 1,
                    'price_unit': 175.0,
                }),
                (0, 0, {
                    'product_id': product_membership_fee.id,
                    'quantity': 1,
                    'price_unit': 300.0,
                }),
            ],
        }
        invoice = self.env['account.move'].sudo().create(invoice_vals)

        # Send Invoice via Email
        invoice.sudo().action_post()  # Post the invoice
        template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
        if template:
            template.sudo().send_mail(invoice.id, force_send=True)

        # Redirect to Invoice Form View
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }

    def action_reject_login(self):
        """To reject the request from website"""
        self.for_approval_menu = False
        self.hide_button = True
        user = self.env['res.users'].sudo().search([('login', '=', self.email)])
        if user:
            user.unlink()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string="Gender")

    birthday = fields.Date(string="Birthday")

    recommended_by = fields.Char(string="Recommended By")