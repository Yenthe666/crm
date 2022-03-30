# -*- coding: utf-8 -*-
{
    'name': "CRM update sales team stages",

    'summary': """
        Create/delete stages for sales teams
    """,

    'description': """
        Create/delete stages for sales teams
    """,

    'author': "Mainframe Monkey",
    'website': "http://www.mainframemonkey.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/CRM',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/actions.xml',
        'views/menus.xml',

        'wizard/crm_team_stage_wizard_views.xml',
    ],

    'license': 'LGPL-3',
}
