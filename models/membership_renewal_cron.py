from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class MembershipRenewalCron(models.Model):
    _name = 'membership.renewal.cron'
    _description = 'Membership Renewal Cron Job'

    @api.model
    def run_membership_renewals(self):
        """Main cron job to handle all membership renewals"""
        try:
            # Check for membership renewals
            self.env['res.users.approve'].check_membership_renewals()

            # Check for expired memberships
            self._check_expired_memberships()

            _logger.info("Membership renewal cron job executed successfully")
        except Exception as e:
            _logger.error(f"Error in membership renewal cron job: {e}")

        return True

    def _check_expired_memberships(self):
        """Check for expired memberships and deactivate them"""
        today = fields.Date.today()
        expired_memberships = self.env['res.users.approve'].search([
            ('membership_status', '=', 'active'),
            ('membership_end_date', '<', today),
            ('cancellation_date', '=', False),
        ])

        for membership in expired_memberships:
            membership.write({
                'membership_status': 'expired',
            })

            # Deactivate user account
            user = self.env['res.users'].search([('login', '=', membership.email)])
            if user:
                user.active = False

            _logger.info(f"Deactivated expired membership for {membership.name}")

    @api.model
    def schedule_renewal_invoice(self, approval, invoice_date):
        """Schedule a renewal invoice for a specific date"""
        # This would be implemented with Odoo's automated actions or queue jobs
        # For simplicity, we'll just log it
        _logger.info(f"Scheduled renewal invoice for {approval.name} on {invoice_date}")
        return True