from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    """Adding field in res config settings"""
    _inherit = 'res.config.settings'

    auth_signup_approval = fields.Boolean(
        string='Signup Approval',
        config_parameter='website_signup_approval.auth_signup_approval',
        help="Signup request requires approval before users can login"
    )
    documents_ids = fields.Many2many(
        'document.attachment',
        string='Required Documents',
        help="Select the types of documents required for signup"
    )

    def set_values(self):
        """Set values for the field"""
        res = super().set_values()
        param = self.env['ir.config_parameter'].sudo()
        documents_ids = self.documents_ids.ids
        param.set_param(
            'website_signup_approval.documents_ids',
            str(documents_ids)
        )
        return res

    def get_values(self):
        """Return values for the fields"""
        res = super().get_values()
        param = self.env['ir.config_parameter'].sudo()
        documents_str = param.get_param('website_signup_approval.documents_ids', '[]')
        try:
            import ast
            documents_ids = ast.literal_eval(documents_str)
            res.update(
                documents_ids=[(6, 0, documents_ids)]
            )
        except:
            res.update(documents_ids=False)
        return res