# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64
import logging
from werkzeug.datastructures import FileStorage

_logger = logging.getLogger(__name__)


class CustomerPortalAttachments(CustomerPortal):

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        """Override account method to handle attachment operations"""

        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        error = {}
        error_message = []

        # Handle form submission
        if post and request.httprequest.method == 'POST':

            _logger.info("=" * 50)
            _logger.info("FORM SUBMITTED - Starting to process attachments")
            _logger.info(f"POST keys: {list(post.keys())}")
            _logger.info(f"FILES keys: {list(request.httprequest.files.keys())}")
            _logger.info("=" * 50)

            # Process existing attachments updates
            for att in partner.attachment_line_ids:
                att_id = att.id

                # Update name if changed
                new_name = post.get(f'attachment_name_{att_id}')
                if new_name and new_name != att.name:
                    try:
                        att.write({'name': new_name})
                    except Exception as e:
                        error_message.append(_('Error updating name for document: %s') % str(e))

                # Update end_date if changed
                new_end_date = post.get(f'end_date_{att_id}')
                if new_end_date:
                    try:
                        att.write({'end_date': new_end_date})
                    except Exception as e:
                        error_message.append(_('Error updating expiry date: %s') % str(e))
                elif f'end_date_{att_id}' in post:
                    # If field exists but is empty, clear the date
                    att.write({'end_date': False})

                # Handle file replacement
                replace_file_key = f'replace_file_{att_id}'
                if replace_file_key in request.httprequest.files:
                    replace_file = request.httprequest.files.get(replace_file_key)
                    if replace_file and isinstance(replace_file, FileStorage) and replace_file.filename:
                        try:
                            _logger.info(f"Replacing file for attachment {att_id}, filename: {replace_file.filename}")

                            file_content = replace_file.read()
                            file_b64 = base64.b64encode(file_content)

                            _logger.info(f"File size: {len(file_content)} bytes")

                            # Method 1: Direct write (if attachment=False in model)
                            att.sudo().write({
                                'attachment_data': file_b64,
                                'attachment_name': replace_file.filename,
                            })

                            # Method 2: If using ir.attachment (if attachment=True in model)
                            # First, delete old attachment if exists
                            # old_attachments = request.env['ir.attachment'].sudo().search([
                            #     ('res_model', '=', 'res.partner.attachment.line'),
                            #     ('res_id', '=', att_id),
                            #     ('res_field', '=', 'attachment_data'),
                            # ])
                            # old_attachments.unlink()
                            #
                            # # Create new attachment
                            # request.env['ir.attachment'].sudo().create({
                            #     'name': replace_file.filename,
                            #     'datas': file_b64,
                            #     'res_model': 'res.partner.attachment.line',
                            #     'res_id': att_id,
                            #     'res_field': 'attachment_data',
                            #     'type': 'binary',
                            # })
                            # att.sudo().write({'attachment_name': replace_file.filename})

                            _logger.info(f"File replacement completed for attachment {att_id}")

                        except Exception as e:
                            _logger.error(f"Error replacing file for attachment {att_id}: {str(e)}", exc_info=True)
                            error_message.append(_('Error replacing file for %s: %s') % (att.name, str(e)))

            new_name = post.get('new_attachment_name', '').strip()
            new_file = None

            if 'new_attachment_file' in request.httprequest.files:
                new_file = request.httprequest.files.get('new_attachment_file')

            if new_name or (new_file and isinstance(new_file, FileStorage) and new_file.filename):
                if new_name and new_file and isinstance(new_file, FileStorage) and new_file.filename:
                    try:
                        file_content = base64.b64encode(new_file.read())
                        new_end_date = post.get('new_end_date', '').strip() or False

                        request.env['res.partner.attachment.line'].sudo().create({
                            'partner_id': partner.id,
                            'name': new_name,
                            'attachment_data': file_content,
                            'attachment_name': new_file.filename,
                            'end_date': new_end_date if new_end_date else False,
                        })
                    except Exception as e:
                        error_message.append(_('Error creating new document: %s') % str(e))
                elif new_name and not (new_file and isinstance(new_file, FileStorage) and new_file.filename):
                    error_message.append(_('Please upload a file for the new document "%s"') % new_name)
                elif (new_file and isinstance(new_file, FileStorage) and new_file.filename) and not new_name:
                    error_message.append(_('Please provide a name for the new document'))


            partner_values = {}

            if 'name' in post:
                partner_values['name'] = post.get('name')
            if 'phone' in post:
                partner_values['phone'] = post.get('phone')
            if 'email' in post:
                partner_values['email'] = post.get('email')
            if 'street' in post:
                partner_values['street'] = post.get('street')
            if 'street2' in post:
                partner_values['street2'] = post.get('street2')
            if 'city' in post:
                partner_values['city'] = post.get('city')
            if 'zipcode' in post:
                partner_values['zip'] = post.get('zipcode')  # Changed from zipcode to zip
            if 'country_id' in post:
                partner_values['country_id'] = int(post.get('country_id')) if post.get('country_id') else False
            if 'state_id' in post:
                partner_values['state_id'] = int(post.get('state_id')) if post.get('state_id') else False
            if 'company_name' in post:
                partner_values['company_name'] = post.get('company_name')
            if 'vat' in post:
                partner_values['vat'] = post.get('vat')

            if partner_values:
                try:
                    partner.sudo().write(partner_values)
                except Exception as e:
                    error_message.append(_('Error updating profile: %s') % str(e))

            if error_message:
                values['error_message'] = error_message
            else:
                return request.redirect('/my/account')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'partner_can_edit_vat': partner.can_edit_vat(),
            'error': error,
            'error_message': error_message,
        })

        return request.render("portal.portal_my_details", values)

    @http.route(['/my/attachments/delete/<int:attachment_id>'], type='http', auth='user', website=True)
    def delete_attachment(self, attachment_id, **kw):
        """Optional: Allow users to delete attachments"""
        partner = request.env.user.partner_id
        attachment = request.env['res.partner.attachment.line'].sudo().search([
            ('id', '=', attachment_id),
            ('partner_id', '=', partner.id)
        ], limit=1)

        if attachment:
            try:
                attachment.unlink()
            except Exception as e:
                pass

        return request.redirect('/my/account')

    @http.route(['/my/attachments/download/<int:attachment_id>'], type='http', auth='user', website=True)
    def download_attachment(self, attachment_id, **kw):
        """Download attachment file"""
        try:
            partner = request.env.user.partner_id
            attachment_line = request.env['res.partner.attachment.line'].sudo().search([
                ('id', '=', attachment_id),
                ('partner_id', '=', partner.id)
            ], limit=1)

            if not attachment_line:
                _logger.warning(f"Attachment {attachment_id} not found or doesn't belong to user")
                return request.not_found()

            _logger.info(f"Downloading attachment {attachment_id} - {attachment_line.attachment_name}")

            if attachment_line.attachment_data:
                _logger.info("Found attachment_data directly in field")
                try:
                    file_content = base64.b64decode(attachment_line.attachment_data)
                    filename = attachment_line.attachment_name or 'download'

                    _logger.info(f"File size: {len(file_content)} bytes, filename: {filename}")

                    headers = [
                        ('Content-Type', 'application/octet-stream'),
                        ('Content-Disposition', f'attachment; filename="{filename}"'),
                        ('Content-Length', len(file_content))
                    ]

                    return request.make_response(file_content, headers=headers)
                except Exception as e:
                    _logger.error(f"Error decoding attachment data: {str(e)}", exc_info=True)

            # Method 2: Try to find in ir.attachment (if attachment=True in model)
            _logger.info("Searching in ir.attachment...")
            ir_attachment = request.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'res.partner.attachment.line'),
                ('res_id', '=', attachment_id),
                ('res_field', '=', 'attachment_data'),
            ], limit=1)

            if ir_attachment:
                _logger.info(f"Found ir.attachment: {ir_attachment.id} - {ir_attachment.name}")
                try:
                    file_content = base64.b64decode(ir_attachment.datas)
                    filename = ir_attachment.name or attachment_line.attachment_name or 'download'

                    headers = [
                        ('Content-Type', ir_attachment.mimetype or 'application/octet-stream'),
                        ('Content-Disposition', f'attachment; filename="{filename}"'),
                        ('Content-Length', len(file_content))
                    ]

                    return request.make_response(file_content, headers=headers)
                except Exception as e:
                    _logger.error(f"Error getting data from ir.attachment: {str(e)}", exc_info=True)

            _logger.error(f"No attachment data found for attachment_id {attachment_id}")
            return request.not_found()

        except Exception as e:
            _logger.error(f"Error in download_attachment: {str(e)}", exc_info=True)
            return request.not_found()