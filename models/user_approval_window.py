from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64


class UserApprovalWindow(models.Model):
    """Store Information of Attachment Field"""
    _name = 'user.approval.window'
    _description = 'Attachment Details in User Approval Window'

    attachments = fields.Binary(string='Attachments', attachment=True,
                                help="Store the uploaded document")

    approval_id = fields.Many2one('res.users.approve',
                                  help="Signup information's of user",
                                  string="Approval ID")

    filename = fields.Char(string="File Name")


    @api.constrains('attachments')
    def _check_attachment_format(self):
        for rec in self:
            if rec.attachments and rec.filename:
                ext = rec.filename.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png']:
                    raise ValidationError(
                        _("Only JPG and PNG images are allowed.")
                    )


class SignupNotification(models.Model):
    _name = 'signup.notification'
    _description = 'Signup Notification Email'

    name = fields.Char(string="Name")
    email = fields.Char(string="Email", required=True)