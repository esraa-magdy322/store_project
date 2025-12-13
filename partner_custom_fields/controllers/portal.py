# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo.exceptions import AccessError
from werkzeug.utils import redirect


class CustomerPortalInherit(CustomerPortal):

    def _get_optional_fields(self):
        """Add expire_date and company_registry to optional fields"""
        optional_fields = super(CustomerPortalInherit, self)._get_optional_fields()
        # Add custom fields to the list of optional fields
        optional_fields.extend(['expire_date', 'company_registry'])
        return optional_fields

    @http.route(['/my/attachments'], type='http', auth='user', website=True)
    def portal_my_attachments(self, **kw):
        """Display user's attachments"""
        partner = request.env.user.partner_id

        # Get attachments for this partner
        attachments = request.env['ir.attachment'].search([
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', partner.id),
        ], order='create_date desc')

        values = {
            'attachments': attachments,
            'page_name': 'attachments',
        }
        return request.render('partner_custom_fields.portal_my_attachments', values)

    @http.route(['/my/attachments/upload'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_my_attachments_upload(self, file=None, description=None, **kw):
        """Upload a new attachment"""
        if not file:
            return redirect('/my/attachments')

        partner = request.env.user.partner_id

        # Read file content
        file_content = file.read()
        file_name = file.filename

        # Create attachment
        request.env['ir.attachment'].sudo().create({
            'name': file_name,
            'description': description or '',
            'datas': base64.b64encode(file_content),
            'res_model': 'res.partner',
            'res_id': partner.id,
            'public': False,
        })

        return redirect('/my/attachments')

    @http.route(['/my/attachments/download/<int:attachment_id>'], type='http', auth='user', website=True)
    def portal_my_attachments_download(self, attachment_id, **kw):
        """Download an attachment"""
        partner = request.env.user.partner_id

        # Check if attachment belongs to this partner
        attachment = request.env['ir.attachment'].sudo().search([
            ('id', '=', attachment_id),
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', partner.id),
        ], limit=1)

        if not attachment:
            return request.redirect('/my/attachments')

        # Return file
        return request.make_response(
            base64.b64decode(attachment.datas),
            headers=[
                ('Content-Type', attachment.mimetype or 'application/octet-stream'),
                ('Content-Disposition', f'attachment; filename="{attachment.name}"'),
            ]
        )

    @http.route(['/my/attachments/delete/<int:attachment_id>'], type='http', auth='user', website=True, methods=['GET'])
    def portal_my_attachments_delete(self, attachment_id, **kw):
        """Delete an attachment"""
        partner = request.env.user.partner_id

        # Check if attachment belongs to this partner
        attachment = request.env['ir.attachment'].sudo().search([
            ('id', '=', attachment_id),
            ('res_model', '=', 'res.partner'),
            ('res_id', '=', partner.id),
        ], limit=1)

        if attachment:
            attachment.unlink()

        return redirect('/my/attachments')
