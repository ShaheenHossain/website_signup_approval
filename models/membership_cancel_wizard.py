from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class MembershipCancelWizard(models.TransientModel):
    _name = 'membership.cancel.wizard'
    _description = 'Membership Cancellation Wizard'

    approval_id = fields.Many2one('res.users.approve', string='Member', required=True)
    cancellation_date = fields.Date(
        string='Cancellation Date',
        required=True,
        default=fields.Date.today
    )
    cancellation_reason = fields.Text(string='Cancellation Reason', required=True)

    def action_confirm_cancellation(self):
        """Confirm membership cancellation"""
        for wizard in self:
            wizard.approval_id.write({
                'membership_status': 'cancelled',
                'cancellation_date': wizard.cancellation_date,
                'cancellation_reason': wizard.cancellation_reason,
            })

            # Send cancellation confirmation
            template = self.env.ref('website_signup_approval.mail_template_membership_cancelled',
                                    raise_if_not_found=False)
            if template:
                template.send_mail(wizard.approval_id.id, force_send=True)

        return {'type': 'ir.actions.act_window_close'}