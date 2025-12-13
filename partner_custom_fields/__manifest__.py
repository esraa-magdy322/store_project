# -*- coding: utf-8 -*-
{
    'name': 'Partner Custom Fields',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Add custom fields to partner form (expire_date and period)',
    'description': """
        This module extends the partner (res.partner) model to add:
        - Expire Date: Date field for tracking expiration
        - Period: Number of days before expiration to send alert
        - Alert Date: Automatically calculated (expire_date - period days)
        - Automatic activity creation for salesperson when alert date is reached
        - Red highlighting of Salesperson field when alert is active

        Fields are positioned after the Company ID field in the form view.
        A scheduled action runs daily to check for partners reaching their alert date.
    """,
    'author': 'BDC Solutions',
    'website': 'https://www.bdc-solutions.com',
    'depends': ['base', 'contacts', 'mail', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_attachment_security.xml',
        'data/ir_cron_data.xml',
        'views/res_partner_views.xml',
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
