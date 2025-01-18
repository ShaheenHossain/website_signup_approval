from email.policy import default

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ResUsersApprove(models.Model):
    """Store Signup Information of Users from Website"""
    _name = 'res.users.approve'
    _description = "Approval Request Details"

    # name = fields.Char(help="Name of the user", string='Name')

    # customer_id = fields.Char(string="Member ID", readonly=True, copy=False)

    customer_id = fields.Many2one('res.partner', string="Customer")

    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    name = fields.Char(string='Full Name', compute='_compute_full_name', store=True)

    company_name = fields.Char(help="Company", string="Company")
    email = fields.Char(help="Email of the user", string="Email")
    password = fields.Char(help="Password of the user", string="Password")

    gender = fields.Selection([
        ('female', 'Female'),
        ('male', 'Male'),
        ('other', 'Other')
    ], string='Gender', default='male')

    birthday = fields.Date(string='Birthday')
    street = fields.Char(string='Street and House Number')
    address_supplement = fields.Char(string='Address Supplement')
    province = fields.Char(string='Canton / Province / Region')
    city = fields.Char(string='City')
    postal_code = fields.Char(string='Postal Code')
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        default=lambda self: self.env.ref('base.ch'))

    phone = fields.Char(string='Phone Number')
    recommended_by = fields.Char(string='Recommended By')
    # recommended_by = fields.Char(string='Recommended By', required=False)
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

    recommended_by_email = fields.Char(string='Recommended By (Email)')
    recommended_by_phone = fields.Char(string='Recommended By (Phone)')

    # @api.model
    # def create(self, vals):
    #     # Generate the customer ID from the sequence
    #     if 'member_id' not in vals or not vals['member_id']:
    #         vals['member_id'] = self.env['ir.sequence'].next_by_code('res.users.approve.id') or _('New')
    #     return super(ResUsersApprove, self).create(vals)



    @api.constrains('recommended_by_email', 'recommended_by_phone')
    def _check_recommendation(self):
        for rec in self:
            if not rec.recommended_by_email and not rec.recommended_by_phone:
                raise ValidationError(_("Please provide either an email or phone number for the recommender."))

            if rec.recommended_by_email:
                user = self.env['res.users'].search([('email', '=', rec.recommended_by_email)], limit=1)
                if not user:
                    raise ValidationError(
                        _("The provided email does not match any existing user. Please verify the email."))

            if rec.recommended_by_phone:
                user = self.env['res.users'].search([('phone', '=', rec.recommended_by_phone)], limit=1)
                if not user:
                    raise ValidationError(
                        _("The provided phone number does not match any existing user. Please verify the phone number."))

    def _compute_full_name(self):
        for rec in self:
            rec.name = f"{rec.first_name or ''} {rec.last_name or ''}".strip()


    def action_reject_login(self):
        """To reject the request from website"""
        self.for_approval_menu = False
        self.hide_button = True
        user = self.env['res.users'].sudo().search([('login', '=', self.email)])
        if user:
            user.unlink()

    #
    # def action_approve_login(self):
    #     """To approve the request from the website and generate an ID."""
    #     # Generate the ID only when approval happens
    #     if not self.customer_id:
    #         self.customer_id = self.env['ir.sequence'].next_by_code('res.users.approve.id') or _('New')
    #
    #     self.for_approval_menu = True
    #     self.hide_button = True
    #
    #     # Approve User Login logic
    #     user = self.env['res.users'].sudo().search([('login', '=', self.email)])
    #     if not user:
    #         user = self.env['res.users'].sudo().create({
    #             'login': self.email,
    #             'name': self.name,
    #             'password': self.password,
    #             'groups_id': [(4, self.env.ref('base.group_portal').id)],
    #         })
    #
    #         # Update partner with relevant data
    #         user.partner_id.sudo().write({
    #             'email': self.email,
    #             'phone': self.phone,
    #             'street': self.street,
    #             'city': self.city,
    #             'zip': self.postal_code,
    #             'country_id': self.country_id.id,
    #         })

    def action_approve_login(self):
        """To approve the request from website and generate invoice without sending it."""
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

        # Define Default Product Names and Prices
        products_data = [
            {'name': 'Admission Fee', 'price': 250.0},
            {'name': 'Membership Fee', 'price': 1750.0},
            {'name': 'Consumption Prepayment', 'price': 1000.0},
        ]

        invoice_lines = []
        for product_data in products_data:
            product = self.env['product.product'].search([('name', '=', product_data['name'])], limit=1)
            if not product:
                # Create product dynamically if it doesn't exist
                product = self.env['product.product'].sudo().create({
                    'name': product_data['name'],
                    'type': 'service',
                    'list_price': product_data['price'],  # Set default price
                })

            # Prepare invoice line
            invoice_lines.append((0, 0, {
                'product_id': product.id,
                'quantity': 1,
                'price_unit': product_data['price'],  # Use dynamic price
            }))

        # Create Invoice without posting or sending
        invoice_vals = {
            'move_type': 'out_invoice',  # Customer Invoice
            'partner_id': user.partner_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines,
        }
        invoice = self.env['account.move'].sudo().create(invoice_vals)

        # Redirect to Invoice Form View
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }

    # @api.model
    # def notify_new_signup(self, signup_details):
    #     message = f"New signup by {signup_details.get('name')} ({signup_details.get('email')})"
    #     self.env['bus.bus']._sendone(
    #         channel="new_signup",
    #         message={"type": "new_signup", "message": message},
    #     )


# three action to reduce the time for process

# def action_approve_user(self):
#     self.for_approval_menu = True
#     self.hide_button = True
#     user = self.env['res.users'].sudo().search([('login', '=', self.email)])
#     if not user:
#         user = self.env['res.users'].sudo().create({
#             'login': self.email,
#             'name': self.name,
#             'password': self.password,
#             'groups_id': [(4, self.env.ref('base.group_portal').id)],
#         })
#         partner = user.partner_id
#         partner.sudo().write({
#             'email': self.email,
#             'phone': self.phone,
#             'street': self.street,
#             'city': self.city,
#             'zip': self.postal_code,
#             'country_id': self.country_id.id,
#         })
#     return True
#
# def action_create_invoice(self):
#     user = self.env['res.users'].sudo().search([('login', '=', self.email)])
#     if not user:
#         raise ValueError("User not found. Please approve the user first.")
#     product_joining_fee = self.env['product.product'].search([('name', '=', 'Admission Fee')], limit=1)
#     product_service_charge = self.env['product.product'].search([('name', '=', 'Membership Fee')], limit=1)
#     product_membership_fee = self.env['product.product'].search([('name', '=', 'Consumption Prepayment')], limit=1)
#     if not product_joining_fee or not product_service_charge or not product_membership_fee:
#         raise ValueError("Required products are missing.")
#     invoice_vals = {
#         'move_type': 'out_invoice',
#         'partner_id': user.partner_id.id,
#         'invoice_date': fields.Date.today(),
#         'invoice_line_ids': [
#             (0, 0, {'product_id': product_joining_fee.id, 'quantity': 1, 'price_unit': 250.0}),
#             (0, 0, {'product_id': product_service_charge.id, 'quantity': 1, 'price_unit': 1750.0}),
#             (0, 0, {'product_id': product_membership_fee.id, 'quantity': 1, 'price_unit': 1000.0}),
#         ],
#     }
#     invoice = self.env['account.move'].sudo().create(invoice_vals)
#     return {
#         'type': 'ir.actions.act_window',
#         'name': 'Invoice',
#         'res_model': 'account.move',
#         'view_mode': 'form',
#         'res_id': invoice.id,
#         'target': 'current',
#     }
#
#
# def action_send_invoice_email(self):
#     invoice = self.env['account.move'].search([('partner_id', '=', self.env['res.partner'].sudo().search([('email', '=', self.email)]).id)], limit=1)
#     if not invoice:
#         raise ValueError("Invoice not found.")
#     invoice.sudo().action_post()
#     template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
#     if template:
#         template.sudo().send_mail(invoice.id, force_send=True)
#     return True

##perfectly work but i need to reduce the process time to remove send email it may reduce the time

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
    #             'groups_id': [(4, self.env.ref('base.group_portal').id)],
    #         })
    #
    #         # Update associated partner with email and phone
    #         partner = user.partner_id
    #         partner.sudo().write({
    #             'email': self.email,
    #             'phone': self.phone,
    #             'street': self.street,
    #             'city': self.city,
    #             'zip': self.postal_code,
    #             'country_id': self.country_id.id,
    #         })
    #
    #         # Send notification email to the new user
    #         template = self.env.ref(
    #             'auth_signup.mail_template_user_signup_account_created',
    #             raise_if_not_found=False)
    #         email_values = {'email_to': user.login}
    #         template.send_mail(user.id, email_values=email_values, force_send=True)
    #
    #     # Define Service Products
    #     product_joining_fee = self.env['product.product'].search([('name', '=', 'Admission Fee')], limit=1)
    #     product_service_charge = self.env['product.product'].search([('name', '=', 'Membership Fee')], limit=1)
    #     product_membership_fee = self.env['product.product'].search([('name', '=', 'Consumption Prepayment')], limit=1)
    #
    #     # Debugging Logs
    #     if not product_joining_fee:
    #         _logger.error("Product 'Admission Fee' is not defined in the database.")
    #     if not product_service_charge:
    #         _logger.error("Product 'Membership Fee' is not defined in the database.")
    #     if not product_membership_fee:
    #         _logger.error("Product 'Consumption Prepayment' is not defined in the database.")
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
    #                 'price_unit': 250.0,
    #             }),
    #             (0, 0, {
    #                 'product_id': product_service_charge.id,
    #                 'quantity': 1,
    #                 'price_unit': 1750.0,
    #             }),
    #             (0, 0, {
    #                 'product_id': product_membership_fee.id,
    #                 'quantity': 1,
    #                 'price_unit': 1000.0,
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
