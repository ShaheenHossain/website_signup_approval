from email.policy import default

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ResUsersApprove(models.Model):
    """Store Signup Information of Users from Website"""
    _name = 'res.users.approve'
    _description = "Approval Request Details"

    # name = fields.Char(help="Name of the user", string='Name')

    # customer_id = fields.Char(string="Member ID", readonly=True, copy=False)

    def check_document_attachment(self):
        """Check if document.attachment with ID 1 exists."""
        document_attachment = self.env['document.attachment'].browse(1)
        if document_attachment.exists():
            _logger.info("Using document attachment: %s", document_attachment.name)
        else:
            _logger.warning("Document Attachment with ID 1 does not exist.")

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

    # image = fields.Image(string='Profile Image')

    recommended_by_email = fields.Char(string='Recommended By (Email)')
    recommended_by_phone = fields.Char(string='Recommended By (Phone)')

    notification_sent = fields.Boolean(string='Notification Sent', default=False)

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

        # Fetch the first attachment (assuming it's the profile image)
        attachment = self.attachment_ids[:1]  # Get the first attachment

        if attachment:
            # Set the attachment as the user's profile image
            user.partner_id.sudo().write({
                'image_1920': attachment.attachments,  # Set as profile image
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