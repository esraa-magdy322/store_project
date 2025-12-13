# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    expire_date = fields.Date(
        string='Expire Date',
        help='Date when the partner registration or contract expires',
        tracking=True,
    )

    period = fields.Integer(
        string='Period',
        help='Number of days before expiration to send alert',
        tracking=True,
        default=30,
    )

    alert_date = fields.Date(
        string='Alert Date',
        compute='_compute_alert_date',
        store=True,
        help='Date when alert should be triggered (expire_date - period days)',
    )

    is_alert_active = fields.Boolean(
        string='Alert Active',
        compute='_compute_is_alert_active',
        store=True,
        help='True if today is >= alert_date and < expire_date',
    )

    alert_activity_created = fields.Boolean(
        string='Alert Activity Created',
        default=False,
        help='Track if alert activity has been created',
    )

    @api.depends('expire_date', 'period')
    def _compute_alert_date(self):
        """Calculate alert date = expire_date - period days"""
        for partner in self:
            if partner.expire_date and partner.period:
                partner.alert_date = partner.expire_date - timedelta(days=partner.period)
            else:
                partner.alert_date = False

    @api.depends('alert_date', 'expire_date')
    def _compute_is_alert_active(self):
        """Check if today is >= alert_date and < expire_date"""
        today = fields.Date.today()
        for partner in self:
            if partner.alert_date and partner.expire_date:
                partner.is_alert_active = partner.alert_date <= today < partner.expire_date
            else:
                partner.is_alert_active = False

    def create_expiration_activity(self):
        """Create activity for salesperson when alert date is reached"""
        ActivityModel = self.env['mail.activity']
        ActivityType = self.env['mail.activity.type'].search([
            ('name', '=', 'To Do')
        ], limit=1)

        if not ActivityType:
            ActivityType = self.env['mail.activity.type'].search([], limit=1)

        for partner in self:
            # Only create activity if:
            # 1. Alert is active
            # 2. Partner has a salesperson (user_id)
            # 3. Activity hasn't been created yet
            if partner.is_alert_active and partner.user_id and not partner.alert_activity_created:
                activity_vals = {
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'res.partner')], limit=1).id,
                    'res_id': partner.id,
                    'activity_type_id': ActivityType.id,
                    'summary': f'Customer Expiration Alert: {partner.name}',
                    'note': f'<p>Customer <strong>{partner.name}</strong> will expire on <strong>{partner.expire_date}</strong>.</p>'
                            f'<p>Please contact the customer to renew their registration/contract.</p>',
                    'user_id': partner.user_id.id,
                    'date_deadline': partner.expire_date,
                }

                ActivityModel.create(activity_vals)
                partner.alert_activity_created = True

    def reset_alert_activity_flag(self):
        """Reset alert activity flag when dates change"""
        for partner in self:
            if not partner.is_alert_active:
                partner.alert_activity_created = False

    @api.model
    def _cron_check_partner_expiration(self):
        """Scheduled action to check for partners reaching alert date"""
        # Find all partners where alert is active but activity not created
        partners_to_alert = self.search([
            ('is_alert_active', '=', True),
            ('alert_activity_created', '=', False),
            ('user_id', '!=', False),
            ('is_company', '=', True),
        ])

        if partners_to_alert:
            partners_to_alert.create_expiration_activity()

        # Reset flag for partners whose alert is no longer active
        partners_to_reset = self.search([
            ('is_alert_active', '=', False),
            ('alert_activity_created', '=', True),
        ])

        if partners_to_reset:
            partners_to_reset.reset_alert_activity_flag()
