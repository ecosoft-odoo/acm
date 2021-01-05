# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'ACM :: Create Invoices Period',
    'version': '12.0.1.0.0',
    'author': 'Ecosoft',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/contract',
    'category': 'Agreement',
    'depends': [
        'acm',
    ],
    'data': [
        'report/report_receipt_acm.xml',
        'wizards/contract_create_invoice_wizards.xml',
        'views/account_views.xml',
    ],
}
