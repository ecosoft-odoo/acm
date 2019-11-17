# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'ACM :: Rental Collection',
    'version': '12.0.1.0.0',
    'author': 'Ecosoft, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/ecosoft-odoo/acm',
    'category': 'Agreement',
    'depends': [
        'acm',
    ],
    'data': [
        'data/paper_format.xml',
        'report/report_templates.xml',
        'report/rental_collect_report.xml',
        'report/report_payment_voucher.xml',
        'report/report.xml',
        'wizard/rental_collect_report_wizards.xml',
    ],
}
