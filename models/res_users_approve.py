from email.policy import default

from odoo import fields, models


class ResUsersApprove(models.Model):
    """Store Signup Information of Users from Website"""
    _name = 'res.users.approve'
    _description = "Approval Request Details"

    name = fields.Char(help="Name of the user", string='Name')
    email = fields.Char(help="Email of the user", string="Email")
    password = fields.Char(help="Password of the user", string="Password")

    gender = fields.Selection([
        ('female', 'Female'),
        ('male', 'Male'),
        ('other', 'Other')
    ], string='Gender', default='male')
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
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

    def action_approve_login(self):
        """To approve the request from website"""
        self.for_approval_menu = True
        self.hide_button = True
        user = self.env['res.users'].sudo().search([('login', '=', self.email)])
        if not user:
            user = self.env['res.users'].sudo().create({
                'login': self.email,
                'name': self.name,
                'password': self.password,
                'groups_id': [(4, self.env.ref('base.group_portal').id)]
            })
            template = self.env.ref(
                'auth_signup.mail_template_user_signup_account_created',
                raise_if_not_found=False)
            email_values = {
                'email_to': user.login, }
            template.send_mail(user.id, email_values=email_values,
                               force_send=True)

    def action_reject_login(self):
        """To reject the request from website"""
        self.for_approval_menu = False
        self.hide_button = True
        user = self.env['res.users'].sudo().search([('login', '=', self.email)])
        if user:
            user.unlink()
