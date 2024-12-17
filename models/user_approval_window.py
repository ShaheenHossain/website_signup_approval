
from odoo import fields, models


class UserApprovalWindow(models.Model):
    """Store Information of Attachment Field"""
    _name = 'user.approval.window'
    _description = 'Attachment Details in User Approval Window'

    attachments = fields.Binary(string='Attachments', attachment=True,
                                help="Store the uploaded document")
    approval_id = fields.Many2one('res.users.approve',
                                  help="Signup information's of user",
                                  string="Approval ID")
