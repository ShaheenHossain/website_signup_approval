# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class DocumentAttachment(models.Model):
    _name = 'document.attachment'
    _description = 'Document Attachment'

    document = fields.Binary(
        string="Attachment",
        attachment=True,
        required=True
    )
    filename = fields.Char(string="File Name")

    @api.constrains('document', 'filename')
    def _check_document_format(self):
        for rec in self:
            if rec.document and rec.filename:
                ext = rec.filename.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png']:
                    raise ValidationError(
                        _("Only JPG and PNG images are allowed.")
                    )