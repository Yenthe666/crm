# -*- coding: utf-8 -*-
{
    'name': "CRM default sales team stages",

    'summary': """
        Allows to configure and generate default stages for new sale teams
        """,

    'description': """
        Allows to configure and generate default stages for new sale teams
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
        'views/res_config_settings_view.xml',
    ],
}
