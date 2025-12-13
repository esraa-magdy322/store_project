# -*- coding: utf-8 -*-
{
    'name': 'Portal User Creator',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Create portal users directly from customer form',
    'description': """
        This module adds a button to the customer form that allows creating
        portal users for customers. If a portal user already exists, it opens
        the existing user record.
    """,
    'author': 'BDC Solutions',
    'depends': ['base', 'sales_team', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
