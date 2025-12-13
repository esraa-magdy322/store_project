# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_create_portal_user(self):
        """Create or open portal user for the customer"""
        self.ensure_one()

        # Check if user already exists for this partner
        existing_user = self.env['res.users'].search([
            ('partner_id', '=', self.id)
        ], limit=1)

        if existing_user:
            # Open existing user in new window (current tab)
            return {
                'name': _('Portal User'),
                'type': 'ir.actions.act_window',
                'res_model': 'res.users',
                'res_id': existing_user.id,
                'view_mode': 'form',
                'target': 'current',
            }

        # Create new portal user
        portal_group = self.env.ref('base.group_portal')

        # Use email if available, otherwise use partner name as login
        login_name = self.email if self.email else f'portal_{self.id}'

        # Create the user
        new_user = self.env['res.users'].create({
            'partner_id': self.id,
            'login': login_name,
            'groups_id': [(6, 0, [portal_group.id])],
        })

        # Open the newly created user in new window (current tab)
        return {
            'name': _('Portal User'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'res_id': new_user.id,
            'view_mode': 'form',
            'target': 'current',
        }
