# -*- coding: utf-8 -*-

from odoo import models, api, _
import base64
import logging

class AccountMoveSend(models.TransientModel):
    _inherit = 'account.move.send'

    @api.model
    def _prepare_invoice_pdf_report(self, invoice, invoice_data):
        if invoice.invoice_pdf_report_id:
            return

        invoice_data['pdf_attachment_values'] = {
            'name': 'FEL ' + invoice.firma_fel,
            'raw': base64.b64decode(invoice.pdf_fel),
            'type': 'binary',
            'mimetype': 'application/pdf',
            'res_model': invoice._name,
            'res_id': invoice.id,
            'res_field': 'invoice_pdf_report_file',
        }