from ast import literal_eval
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Adding field in res config settings"""
    _inherit = 'res.config.settings'

    auth_signup_approval = fields.Boolean(string='Signup Approval',
                                          config_parameter='website_signup_approval.auth_signup_approval',
                                          help="Signup request send only if "
                                               "it is enabled")
    documents_ids = fields.Many2many('document.attachment',
                                     string='Documents',
                                     help="Select the type of document")

    def set_values(self):
        """Set values for the field"""
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'website_signup_approval.documents_ids',
            self.documents_ids.ids)

    def get_values(self):
        """Return values for the fields"""
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        limits = params.get_param(
            'website_signup_approval.documents_ids')
        res.update(documents_ids=[
            (6, 0, literal_eval(limits))] if limits else False)
        return res
