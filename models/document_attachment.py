# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Vishnu KP @ Cybrosys, (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models


class DocumentAttachment(models.Model):
    """Store Information of Attachment"""
    _name = "document.attachment"
    _description = 'Signup Attachments'
    _rec_name = 'document'

    document = fields.Char(string="Attachment", help="It identify the type of user document")
    name = fields.Char(string="Name", help="Name of the attachment")

    def some_method(self):
        document_attachment = self.env['document.attachment'].browse(1)
        if document_attachment.exists():
            # Use the record
            _logger.info("Using document attachment: %s", document_attachment.name)
        else:
            _logger.warning("Document Attachment with ID 1 does not exist.")

