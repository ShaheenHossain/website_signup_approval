# from email.policy import default
#
# from odoo import fields, models, api, _
# from odoo.exceptions import ValidationError
#
# class ResUsersApprove(models.Model):
#     """Store Signup Information of Users from Website"""
#     _name = 'res.users.approve'
#     _description = "Approval Request Details"
#
#     # name = fields.Char(help="Name of the user", string='Name')
#
#     # customer_id = fields.Char(string="Member ID", readonly=True, copy=False)
#
#     def check_document_attachment(self):
#         """Check if document.attachment with ID 1 exists."""
#         document_attachment = self.env['document.attachment'].browse(1)
#         if document_attachment.exists():
#             _logger.info("Using document attachment: %s", document_attachment.name)
#         else:
#             _logger.warning("Document Attachment with ID 1 does not exist.")
#
#     customer_id = fields.Many2one('res.partner', string="Customer")
#
#     first_name = fields.Char(string='First Name')
#     last_name = fields.Char(string='Last Name')
#     name = fields.Char(string='Full Name', compute='_compute_full_name', store=True)
#
#     company_name = fields.Char(help="Company", string="Company")
#     email = fields.Char(help="Email of the user", string="Email")
#     password = fields.Char(help="Password of the user", string="Password")
#
#     gender = fields.Selection([
#         ('female', 'Female'),
#         ('male', 'Male'),
#         ('other', 'Other')
#     ], string='Gender', default='male')
#
#     birthday = fields.Date(string='Birthday')
#     street = fields.Char(string='Street and House Number')
#     address_supplement = fields.Char(string='Address Supplement')
#     province = fields.Char(string='Canton / Province / Region')
#     city = fields.Char(string='City')
#     postal_code = fields.Char(string='Postal Code')
#     country_id = fields.Many2one(
#         'res.country',
#         string='Country',
#         default=lambda self: self.env.ref('base.ch'))
#
#     phone = fields.Char(string='Phone Number')
#     recommended_by = fields.Char(string='Recommended By')
#     # recommended_by = fields.Char(string='Recommended By', required=False)
#     accept_terms = fields.Boolean(string='Accept Terms and Conditions')
#
#     for_approval_menu = fields.Boolean(string='For Approval Menu',
#                                        default=False,
#                                        help="Check the request is approved")
#     approved_date = fields.Datetime(string='Approved Date', copy=False,
#                                     help="Approval date of signup request")
#     attachment_ids = fields.One2many('user.approval.window',
#                                      'approval_id',
#                                      string='Attachments',
#                                      help="Store uploaded document")
#     hide_button = fields.Boolean(string='For hide button',
#                                  default=False,
#                                  help="Check the button is used or not")
#
#     # image = fields.Image(string='Profile Image')
#
#     recommended_by_email = fields.Char(string='Recommended By (Email)')
#     recommended_by_phone = fields.Char(string='Recommended By (Phone)')
#
#     notification_sent = fields.Boolean(string='Notification Sent', default=False)
#
#     @api.constrains('recommended_by_email', 'recommended_by_phone')
#     def _check_recommendation(self):
#         for rec in self:
#             if not rec.recommended_by_email and not rec.recommended_by_phone:
#                 raise ValidationError(_("Please provide either an email or phone number for the recommender."))
#
#             if rec.recommended_by_email:
#                 user = self.env['res.users'].search([('email', '=', rec.recommended_by_email)], limit=1)
#                 if not user:
#                     raise ValidationError(
#                         _("The provided email does not match any existing user. Please verify the email."))
#
#             if rec.recommended_by_phone:
#                 user = self.env['res.users'].search([('phone', '=', rec.recommended_by_phone)], limit=1)
#                 if not user:
#                     raise ValidationError(
#                         _("The provided phone number does not match any existing user. Please verify the phone number."))
#
#     def _compute_full_name(self):
#         for rec in self:
#             rec.name = f"{rec.first_name or ''} {rec.last_name or ''}".strip()
#
#     def action_reject_login(self):
#         """To reject the request from website"""
#         self.for_approval_menu = False
#         self.hide_button = True
#         user = self.env['res.users'].sudo().search([('login', '=', self.email)])
#         if user:
#             user.unlink()
#
#     def action_approve_login(self):
#         """To approve the request from website and generate invoice without sending it."""
#         self.for_approval_menu = True
#         self.hide_button = True
#
#         # Approve User Login
#         user = self.env['res.users'].sudo().search([('login', '=', self.email)])
#         if not user:
#             user = self.env['res.users'].sudo().create({
#                 'login': self.email,
#                 'name': self.name,
#                 'password': self.password,
#                 'groups_id': [(4, self.env.ref('base.group_portal').id)],
#             })
#
#         # Fetch the first attachment (assuming it's the profile image)
#         attachment = self.attachment_ids[:1]  # Get the first attachment
#
#         if attachment:
#             # Set the attachment as the user's profile image
#             user.partner_id.sudo().write({
#                 'image_1920': attachment.attachments,  # Set as profile image
#                 'email': self.email,
#                 'phone': self.phone,
#                 'street': self.street,
#                 'city': self.city,
#                 'zip': self.postal_code,
#                 'country_id': self.country_id.id,
#             })
#
#         # Define Default Product Names and Prices
#         products_data = [
#             {'name': 'Admission Fee', 'price': 250.0},
#             {'name': 'Membership Fee', 'price': 1750.0},
#             {'name': 'Consumption Prepayment', 'price': 1000.0},
#         ]
#
#         invoice_lines = []
#         for product_data in products_data:
#             product = self.env['product.product'].search([('name', '=', product_data['name'])], limit=1)
#             if not product:
#                 # Create product dynamically if it doesn't exist
#                 product = self.env['product.product'].sudo().create({
#                     'name': product_data['name'],
#                     'type': 'service',
#                     'list_price': product_data['price'],  # Set default price
#                 })
#
#             # Prepare invoice line
#             invoice_lines.append((0, 0, {
#                 'product_id': product.id,
#                 'quantity': 1,
#                 'price_unit': product_data['price'],  # Use dynamic price
#             }))
#
#         # Create Invoice without posting or sending
#         invoice_vals = {
#             'move_type': 'out_invoice',  # Customer Invoice
#             'partner_id': user.partner_id.id,
#             'invoice_date': fields.Date.today(),
#             'invoice_line_ids': invoice_lines,
#         }
#         invoice = self.env['account.move'].sudo().create(invoice_vals)
#
#         # Redirect to Invoice Form View
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Invoice',
#             'res_model': 'account.move',
#             'view_mode': 'form',
#             'res_id': invoice.id,
#             'target': 'current',
#         }


from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResUsersApprove(models.Model):
    """Store Signup Information of Users from Website"""
    _name = 'res.users.approve'
    _description = "Approval Request Details"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    def _get_can_approve(self):
        """Determine if approve/reject buttons should be visible"""
        for rec in self:
            rec.can_approve = not rec.hide_button and not rec.for_approval_menu

    can_approve = fields.Boolean(
        string="Can Approve",
        compute='_get_can_approve',
        store=False
    )

    def _get_can_suspend(self):
        """Determine if suspend button should be visible"""
        for rec in self:
            rec.can_suspend = rec.membership_status == 'active' and rec.for_approval_menu

    can_suspend = fields.Boolean(
        string="Can Suspend",
        compute='_get_can_suspend',
        store=False
    )

    def _get_can_resume(self):
        """Determine if resume button should be visible"""
        for rec in self:
            rec.can_resume = rec.membership_status == 'suspended'

    can_resume = fields.Boolean(
        string="Can Resume",
        compute='_get_can_resume',
        store=False
    )

    def _get_can_cancel(self):
        """Determine if cancel button should be visible"""
        for rec in self:
            rec.can_cancel = rec.membership_status not in ['cancelled', 'expired'] and rec.for_approval_menu

    can_cancel = fields.Boolean(
        string="Can Cancel",
        compute='_get_can_cancel',
        store=False
    )

    def _get_can_renew(self):
        """Determine if renew button should be visible"""
        for rec in self:
            rec.can_renew = rec.membership_status == 'active'

    can_renew = fields.Boolean(
        string="Can Renew",
        compute='_get_can_renew',
        store=False
    )

    #
    #
    # @api.model
    # def _update_existing_members(self):
    #     """Update existing approved members with default membership data"""
    #     try:
    #         # Find all existing approved members
    #         approved_members = self.search([
    #             ('for_approval_menu', '=', True),
    #             ('membership_status', '=', 'draft'),  # Only update draft status
    #         ])
    #
    #         if approved_members:
    #             default_start_date = date(2025, 2, 11)
    #             default_end_date = date(2026, 2, 11)
    #
    #             for member in approved_members:
    #                 member.write({
    #                     'membership_status': 'active',
    #                     'membership_start_date': default_start_date,
    #                     'membership_end_date': default_end_date,
    #                 })
    #
    #             _logger.info(f"Updated {len(approved_members)} existing approved members")
    #     except Exception as e:
    #         _logger.error(f"Error updating existing members: {e}")
    #
    # # Call this method when module is installed/updated
    # @api.model
    # def init(self):
    #     """Initialize module - update existing records"""
    #     super().init()
    #     self._update_existing_members()



    # Basic fields
    customer_id = fields.Many2one('res.partner', string="Customer")
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    name = fields.Char(string='Full Name', compute='_compute_full_name', store=True)
    company_name = fields.Char(help="Company", string="Company")
    email = fields.Char(help="Email of the user", string="Email")
    password = fields.Char(help="Password of the user", string="Password")

    # Membership fields
    membership_start_date = fields.Date(
        string='Membership Start Date',
        tracking=True,
        help="Date when membership becomes active"
    )
    membership_end_date = fields.Date(
        string='Membership End Date',
        tracking=True,
        help="Date when membership expires"
    )
    membership_renewal_date = fields.Date(
        string='Next Renewal Date',
        compute='_compute_renewal_date',
        store=True,
        help="Date when next invoice should be sent"
    )
    membership_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired')
    ], string='Membership Status', default='draft', tracking=True)

    # Cancellation fields
    cancellation_date = fields.Date(string='Cancellation Date')
    cancellation_reason = fields.Text(string='Cancellation Reason')

    # Invoice fields
    membership_invoice_id = fields.Many2one(
        'account.move',
        string='Current Membership Invoice'
    )
    next_invoice_date = fields.Date(
        string='Next Invoice Date',
        compute='_compute_next_invoice_date',
        store=True
    )

    # Other existing fields
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
    accept_terms = fields.Boolean(string='Accept Terms and Conditions')

    for_approval_menu = fields.Boolean(
        string='For Approval Menu',
        default=False,
        help="Check the request is approved"
    )
    approved_date = fields.Datetime(
        string='Approved Date',
        copy=False,
        help="Approval date of signup request"
    )
    attachment_ids = fields.One2many(
        'user.approval.window',
        'approval_id',
        string='Attachments',
        help="Store uploaded document"
    )
    hide_button = fields.Boolean(
        string='For hide button',
        default=False,
        help="Check the button is used or not"
    )

    recommended_by_email = fields.Char(string='Recommended By (Email)')
    recommended_by_phone = fields.Char(string='Recommended By (Phone)')
    notification_sent = fields.Boolean(string='Notification Sent', default=False)

    @api.depends('first_name', 'last_name')
    def _compute_full_name(self):
        for rec in self:
            rec.name = f"{rec.first_name or ''} {rec.last_name or ''}".strip()

    @api.depends('membership_end_date')
    def _compute_renewal_date(self):
        for rec in self:
            if rec.membership_end_date:
                # 3 months before end date
                renewal_date = rec.membership_end_date - relativedelta(months=3)
                rec.membership_renewal_date = renewal_date
            else:
                rec.membership_renewal_date = False

    @api.depends('membership_end_date')
    def _compute_next_invoice_date(self):
        for rec in self:
            if rec.membership_end_date:
                # 3 months before end date
                next_invoice = rec.membership_end_date - relativedelta(months=3)
                rec.next_invoice_date = next_invoice
            else:
                rec.next_invoice_date = False

    def action_reject_login(self):
        """To reject the request from website"""
        for rec in self:
            rec.for_approval_menu = False
            rec.hide_button = True
            user = self.env['res.users'].sudo().search([('login', '=', rec.email)])
            if user:
                user.unlink()

            # Send rejection email if needed
            template = self.env.ref('website_signup_approval.mail_template_signup_rejected', raise_if_not_found=False)
            if template:
                template.sudo().send_mail(rec.id, force_send=True)

        return True

    def action_suspend_membership(self):
        """Suspend membership manually"""
        for rec in self:
            rec.membership_status = 'suspended'
            _logger.info(f"Membership suspended for {rec.name}")
        return True

    def action_resume_membership(self):
        """Resume suspended membership"""
        for rec in self:
            if rec.membership_status == 'suspended':
                # Calculate remaining days and adjust end date
                suspension_days = (fields.Date.today() - rec.membership_start_date).days
                new_end_date = rec.membership_end_date + relativedelta(days=suspension_days)

                rec.write({
                    'membership_status': 'active',
                    'membership_end_date': new_end_date
                })
                _logger.info(f"Membership resumed for {rec.name}, new end date: {new_end_date}")
        return True

    def action_cancel_membership(self):
        """Cancel membership - opens wizard"""
        return {
            'name': _('Cancel Membership'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'membership.cancel.wizard',
            'target': 'new',
            'context': {
                'default_approval_id': self.id,
            }
        }

    def action_renew_membership(self):
        """Manually renew membership for another year"""
        for rec in self:
            if rec.membership_status == 'active':
                # Extend end date by 1 year
                new_end_date = rec.membership_end_date + relativedelta(years=1)
                rec.write({
                    'membership_end_date': new_end_date
                })

                # Create renewal invoice
                rec._create_renewal_invoice()
                _logger.info(f"Renewed membership for {rec.name} until {new_end_date}")
        return True

    def _set_membership_dates(self, start_date=None):
        """Set membership dates based on the provided start date"""
        for rec in self:
            if not start_date:
                start_date = fields.Date.today()

            # Set start date
            rec.membership_start_date = start_date

            # Set end date (1 year from start)
            end_date = start_date + relativedelta(years=1)
            rec.membership_end_date = end_date

            # Set status to active
            rec.membership_status = 'active'

            _logger.info(f"Set membership dates for {rec.name}: Start={start_date}, End={end_date}")

    def action_approve_login(self):
        """To approve the request from website and generate invoice without sending it."""
        self.for_approval_menu = True
        self.hide_button = True
        self.approved_date = fields.Datetime.now()

        # Approve User Login
        user = self.env['res.users'].sudo().search([('login', '=', self.email)])
        if not user:
            user = self.env['res.users'].sudo().create({
                'login': self.email,
                'name': self.name,
                'password': self.password,
                'groups_id': [(4, self.env.ref('base.group_portal').id)],
            })

        # Set membership dates (starts today)
        self._set_membership_dates(fields.Date.today())

        # Fetch the first attachment (assuming it's the profile image)
        attachment = self.attachment_ids[:1]  # Get the first attachment

        if attachment:
            # Set the attachment as the user's profile image
            user.partner_id.sudo().write({
                'image_1920': attachment.attachments,
                'email': self.email,
                'phone': self.phone,
                'street': self.street,
                'city': self.city,
                'zip': self.postal_code,
                'country_id': self.country_id.id,
            })

        # Create customer/partner record
        partner = user.partner_id
        self.customer_id = partner.id

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
                    'list_price': product_data['price'],
                })

            # Prepare invoice line
            invoice_lines.append((0, 0, {
                'product_id': product.id,
                'quantity': 1,
                'price_unit': product_data['price'],
                'name': f"Membership - {product_data['name']}",
            }))

        # Create Invoice without posting or sending
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines,
        }
        invoice = self.env['account.move'].sudo().create(invoice_vals)

        # Store invoice reference
        self.membership_invoice_id = invoice.id

        # Send approval confirmation
        template = self.env.ref('website_signup_approval.mail_template_signup_approved', raise_if_not_found=False)
        if template:
            template.sudo().send_mail(self.id, force_send=True)

        # Redirect to Invoice Form View
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }

    def _create_renewal_invoice(self):
        """Create renewal invoice for membership"""
        for rec in self:
            partner = rec.customer_id or self.env['res.partner'].search([
                ('email', '=', rec.email)
            ], limit=1)

            if not partner:
                _logger.error(f"No partner found for {rec.name}")
                return

            # Create renewal invoice
            product = self.env['product.product'].search([
                ('name', '=', 'Membership Fee')
            ], limit=1)

            if not product:
                product = self.env['product.product'].create({
                    'name': 'Membership Fee',
                    'type': 'service',
                    'list_price': 1750.0,
                })

            invoice_lines = [(0, 0, {
                'product_id': product.id,
                'quantity': 1,
                'price_unit': product.list_price,
                'name': f"Membership Renewal - Year {fields.Date.today().year + 1}",
            })]

            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_date': fields.Date.today(),
                'invoice_line_ids': invoice_lines,
            }

            invoice = self.env['account.move'].create(invoice_vals)
            rec.membership_invoice_id = invoice

            # Send invoice email
            template = self.env.ref('website_signup_approval.mail_template_membership_renewal',
                                    raise_if_not_found=False)
            if template:
                template.send_mail(rec.id, force_send=True)

            _logger.info(f"Created renewal invoice for {rec.name}")

    @api.model
    def check_membership_renewals(self):
        """Cron job to check for membership renewals"""
        today = fields.Date.today()

        # Find memberships that need renewal (3 months before end date)
        memberships = self.search([
            ('membership_status', '=', 'active'),
            ('membership_renewal_date', '<=', today),
            ('cancellation_date', '=', False),
        ])

        for membership in memberships:
            # Create renewal invoice
            membership._create_renewal_invoice()
            _logger.info(f"Scheduled renewal invoice for {membership.name}")

        # Check for upcoming cancellations
        self._check_upcoming_cancellations()

        return True

    def _check_upcoming_cancellations(self):
        """Send warning emails for upcoming cancellations"""
        today = fields.Date.today()

        # Check for cancellations 1 month away
        one_month_later = today + relativedelta(months=1)
        memberships = self.search([
            ('membership_status', '=', 'cancelled'),
            ('cancellation_date', '=', one_month_later),
        ])

        for membership in memberships:
            template = self.env.ref('website_signup_approval.mail_template_cancellation_warning_1month',
                                    raise_if_not_found=False)
            if template:
                template.send_mail(membership.id, force_send=True)

        # Check for cancellations 7 days away
        seven_days_later = today + relativedelta(days=7)
        memberships = self.search([
            ('membership_status', '=', 'cancelled'),
            ('cancellation_date', '=', seven_days_later),
        ])

        for membership in memberships:
            template = self.env.ref('website_signup_approval.mail_template_cancellation_warning_7days',
                                    raise_if_not_found=False)
            if template:
                template.send_mail(membership.id, force_send=True)

        # Check for cancellations 1 day away
        one_day_later = today + relativedelta(days=1)
        memberships = self.search([
            ('membership_status', '=', 'cancelled'),
            ('cancellation_date', '=', one_day_later),
        ])

        for membership in memberships:
            template = self.env.ref('website_signup_approval.mail_template_cancellation_warning_1day',
                                    raise_if_not_found=False)
            if template:
                template.send_mail(membership.id, force_send=True)

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

