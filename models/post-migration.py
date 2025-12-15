from odoo import api, SUPERUSER_ID
from datetime import date


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Set February 11, 2025 as start date for all existing approved members
    existing_approved = env['res.users.approve'].search([
        ('for_approval_menu', '=', True),
        ('membership_start_date', '=', False)
    ])

    default_start_date = date(2025, 2, 11)
    default_end_date = date(2026, 2, 11)

    for member in existing_approved:
        member.write({
            'membership_start_date': default_start_date,
            'membership_end_date': default_end_date,
            'membership_status': 'active',
        })

    print(f"Updated {len(existing_approved)} existing members with default membership dates.")