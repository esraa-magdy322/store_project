# models/res_partner_attachment.py
from odoo import models, fields, api


class ResPartnerAttachment(models.Model):
    _name = 'res.partner.attachment.line'
    _description = 'Partner Attachment Line'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade')
    name = fields.Char(string='Name', required=True)

    attachment_data = fields.Binary(string='Attachment', attachment=True)
    attachment_name = fields.Char(string='File Name')

    end_date = fields.Date(string='End Date')

    file_size = fields.Integer(string='File Size', compute='_compute_file_size', store=True)

    @api.depends('attachment_data')
    def _compute_file_size(self):
        for record in self:
            if record.attachment_data:
                record.file_size = len(record.attachment_data)
            else:
                record.file_size = 0


class ResPartner(models.Model):
    _inherit = 'res.partner'

    attachment_line_ids = fields.One2many(
        'res.partner.attachment.line',
        'partner_id',
        string='Attachments'
    )