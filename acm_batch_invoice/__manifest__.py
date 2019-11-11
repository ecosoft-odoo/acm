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
    ],
    'data': [
        'data/batch_invoice_sequence.xml',
        'security/ir.model.access.csv',
        'views/acm_batch_invoice_views.xml',
        'views/account_invoice_view.xml',
        'report/report_batch_invoice.xml',
        'report/report.xml',
    ],
}
