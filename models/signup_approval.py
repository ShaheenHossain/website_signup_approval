
from odoo import fields, models


class SignupApproval(models.Model):
    """Store Information's of User"""
    _name = 'signup.approval'
    _description = "Approval Request Details"

    login = fields.Char(string='Email', help="Login details of user")
    name = fields.Char(string='Name', help="Name of the user")

    approved_date = fields.Datetime(string='Approved Date', copy=False,
                                    help="Approval date of signup request")
    for_approval_menu = fields.Boolean(string='For Approval Menu',
                                       help="Check the request is approved")

    # def action_approve_login(self):
    #     """To approve the request from website"""
    #     self.env['res.users'].create({
    #         'name': self.name,
    #         'login': self.login,
    #     })
    #     self.env.ref('base.group_user').users.ids.pop()

    def action_approve_login(self):
        """To approve the request from website and generate invoice without sending it."""
        self.for_approval_menu = True
        self.hide_button = True

        # ✅ DO NOT overwrite manually entered approved date
        if not self.approved_date:
            self.approved_date = fields.Datetime.now()
