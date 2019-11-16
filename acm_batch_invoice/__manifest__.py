# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'ACM :: Batch Invoice',
    'version': '12.0.1.0.0',
    'author': 'Ecosoft, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/ecosoft-odoo/acm',
    'category': 'Agreement',
    'depends': [
        'acm',
        'date_range',
        'excel_import_export',
    ],
    'data': [
        'data/batch_invoice_sequence.xml',
        'data/date_range.xml',
        'data/product.xml',
        'security/ir.model.access.csv',
        'wizard/acm_batch_invoice_wizard.xml',
        'views/acm_batch_invoice_views.xml',
        'report/report_batch_invoice.xml',
        'report/report.xml',
        # Excel Import/Export
        'acm_batch_invoice_import_export/actions.xml',
        'acm_batch_invoice_import_export/templates.xml',
    ],
}
