# -- coding: utf-8 --
{
    'name': 'Lead Stage Email Reminders',
    'summary': 'Lead Mail Rule In CRM Lead',
    'description': 'Lead Mail Rule In CRM Lead',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/CRM',
    'version': '14.0.0.1',
    'website': 'https://www.mainframemonkey.com',
    'author': 'Mainframe Monkey',
    'depends': ['crm', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_stage_views.xml',
        'views/crm_team_views.xml',
        'views/lead_mail_rule_views.xml',
        'data/lead_mail_rule_cron.xml',
    ],

    'installable': True,
}
