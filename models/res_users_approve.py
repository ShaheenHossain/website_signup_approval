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



    def send_expiry_reminders(self):
        """Automatically send email reminders before membership expires"""
        today = fields.Date.today()

        reminder_map = {
            3: 'website_signup_approval.mail_template_warning_3months',
            1: 'website_signup_approval.mail_template_warning_1month',
            7: 'website_signup_approval.mail_template_warning_7days',
            0: 'website_signup_approval.mail_template_warning_1day',
        }

        for key, template_xmlid in reminder_map.items():
            # Calculate target date
            if key >= 1:  # months
                target_date = today + relativedelta(months=key)
            else:  # days
                target_date = today + timedelta(days=key)

            memberships = self.search([
                ('membership_status', '=', 'active'),
                ('membership_end_date', '=', target_date)
            ])

            template = self.env.ref(template_xmlid, raise_if_not_found=False)
            if not template:
                _logger.warning("Email template %s not found", template_xmlid)
                continue

            admin_users = self.env['res.users'].search([('share', '=', False), ('active', '=', True)])

            for rec in memberships:
                # Send email to customer
                template.send_mail(rec.id, force_send=True, raise_exception=False)

                # Send copy to all admin users
                for admin in admin_users:
                    template.with_context(force_email=True).send_mail(
                        rec.id, email_values={'email_to': admin.email}, raise_exception=False
                    )

                _logger.info("Sent expiry reminder for %s using template %s", rec.name, template_xmlid)

    def send_renewal_3months(self):
        return self._open_email_template(
            'website_signup_approval.mail_template_warning_3months'
        )

    def send_warning_1month(self):
        return self._open_email_template(
            'website_signup_approval.mail_template_warning_1month'
        )

    def send_warning_7days(self):
        return self._open_email_template(
            'website_signup_approval.mail_template_warning_7days'
        )

    def send_warning_1day(self):
        return self._open_email_template(
            'website_signup_approval.mail_template_warning_1day'
        )


    def send_cancellation_confirmation(self):
        return self._open_email_template(
            'website_signup_approval.mail_template_membership_cancelled'
        )

    def _open_email_template(self, template_xmlid):
        self.ensure_one()

        template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if not template:
            raise ValidationError(_("Email template not found."))

        partner_ids = []
        if self.customer_id:
            partner_ids = [self.customer_id.id]

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model': 'res.users.approve',
                'default_res_ids': [self.id],  # ✅ MUST be list
                'default_use_template': True,
                'default_template_id': template.id,
                'default_partner_ids': partner_ids,
            }
        }


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

    @api.onchange('approved_date')
    def _onchange_approved_date(self):
        for rec in self:
            if rec.approved_date:
                start_date = rec.approved_date.date()
                rec.membership_start_date = start_date
                rec.membership_end_date = start_date + relativedelta(years=1)



    def action_fix_old_membership_dates(self):
        records = self.search([
            ('approved_date', '=', False),
            ('create_date', '!=', False)
        ])

        for rec in records:
            approved = rec.create_date

            if approved:
                start_date = approved.date()

                rec.write({
                    'approved_date': approved,
                    'membership_start_date': start_date,
                    'membership_end_date': start_date + relativedelta(years=1),
                })




    @api.onchange('membership_start_date')
    def _onchange_membership_start_date(self):
        for rec in self:
            if rec.membership_start_date:
                end_date = rec.membership_start_date + relativedelta(years=1)

                rec.membership_end_date = end_date
                rec.membership_renewal_date = end_date
            else:
                rec.membership_end_date = False
                rec.membership_renewal_date = False

    #
    # membership_status = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('pending', 'Pending Approval'),
    #     ('active', 'Active'),
    #     ('suspended', 'Suspended'),
    #     ('cancelled', 'Cancelled'),
    #     ('expired', 'Expired')
    # ], string='Membership Status', default='draft', tracking=True)


    membership_status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ], compute='_compute_membership_status_from_invoice', store=True)



    # Cancellation fields
    cancellation_date = fields.Date(string='Cancellation Date')
    cancellation_reason = fields.Text(string='Cancellation Reason')

    # Invoice fields
    membership_invoice_id = fields.Many2one(
        'account.move',
        string='Current Membership Invoice'
    )

    # next_invoice_date = fields.Date(
    #     string='Next Invoice Date',
    #     compute='_compute_next_invoice_date',
    #     store=True
    # )
    #
    # next_invoice_date = fields.Date(
    #     string='Next Invoice Date',
    #     related='membership_renewal_date',
    #     store=True,
    #     readonly=True
    # )


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

    # @api.depends('membership_end_date')
    # def _compute_next_invoice_date(self):
    #     for rec in self:
    #         if rec.membership_end_date:
    #             # 3 months before end date
    #             next_invoice = rec.membership_end_date - relativedelta(months=3)
    #             rec.next_invoice_date = next_invoice
    #         else:
    #             rec.next_invoice_date = False

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


    @api.depends(
        'membership_invoice_id.state',
        'membership_invoice_id.payment_state'
    )
    def _compute_membership_status_from_invoice(self):
        for rec in self:

            invoice = rec.membership_invoice_id

            if not invoice:
                rec.membership_status = 'draft'
                continue

            # ✅ Logger is good – keep it
            _logger.info(
                "Checking invoice %s | state=%s | payment_state=%s",
                invoice.id,
                invoice.state,
                invoice.payment_state
            )

            # Draft invoice → Pending
            if invoice.state == 'draft':
                rec.membership_status = 'pending'
                continue

            # ✅ Active if IN PAYMENT or PAID
            if invoice.payment_state in ('in_payment', 'paid'):
                rec.membership_status = 'active'

                # Set membership dates only first time
                if not rec.membership_start_date:
                    start_date = invoice.invoice_date or fields.Date.today()
                    rec.membership_start_date = start_date
                    rec.membership_end_date = start_date + relativedelta(years=1)

                continue

            # Posted but NOT paid
            if invoice.state == 'posted' and invoice.payment_state == 'not_paid':
                rec.membership_status = 'pending'
                continue

            # Fallback safety
            rec.membership_status = 'pending'


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


