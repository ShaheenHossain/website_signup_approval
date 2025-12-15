from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import base64


class AttachmentReplaceWizard(models.TransientModel):
    _name = 'attachment.replace.wizard'
    _description = 'Replace Attachment with Image Wizard'

    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Attachment',
        required=True
    )

    customer_name = fields.Char(string='Customer', readonly=True)

    new_image = fields.Binary(
        string='New Image File',
        required=True,
        help="Upload a JPG or PNG image"
    )

    file_name = fields.Char(string='File Name')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        attachment_id = self._context.get('default_attachment_id')
        if attachment_id:
            attachment = self.env['ir.attachment'].browse(attachment_id)
            res.update({
                'customer_name': attachment.res_id and attachment.name or '',
                'file_name': attachment.name,
            })
        return res

    def action_replace(self):
        self.ensure_one()

        # Validate image type
        file_data = base64.b64decode(self.new_image or b'')
        if not (
            file_data.startswith(b'\xff\xd8\xff') or
            file_data.startswith(b'\x89PNG')
        ):
            raise ValidationError(_("Only JPG or PNG images are allowed."))

        # Replace attachment content
        self.attachment_id.write({
            'datas': self.new_image,
            'mimetype': 'image/jpeg',
            'name': self.file_name or self.attachment_id.name,
        })

        return {'type': 'ir.actions.act_window_close'}
