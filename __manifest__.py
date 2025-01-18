{
    'name': "Website Signup Approval",
    'version': '17.0.1.0.3',
    'summary': 'Approve signup request to login to the website',
    'description': """This module approve or reject signup approval request of 
     users from website.User can upload their documents for approval.""",
    'author': "Cybrosys Techno Solutions",
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'category': 'Website',
    'depends': ['website_sale'],
    'data': [
        'security/website_signup_approval_groups.xml',
        'security/ir.model.access.csv',
        # 'data/website_signup_approval_data.xml',
        'views/res_users_approve_views.xml',
        'views/res_config_settings_views.xml',
        'views/signup_templates.xml',
        'views/document_attachment_views.xml',
        'views/approval_request_templates.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'website_signup_approval/static/src/js/signup.js'
            # 'website_signup_approval/static/src/js/new_signup_notification.js'
            # 'website_signup_approval/static/src/scss/custom_login.scss'
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
