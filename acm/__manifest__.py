# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'ACM :: Agreement Contract',
    'version': '12.0.1.0.0',
    'author': 'Ecosoft, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/contract',
    'category': 'Agreement',
    'depends': [
        'agreement_legal',
        'contract',
    ],
    'data': [
        'acm_agreement_contract/data/report_paperformat_data.xml',
        'acm_agreement_contract/data/report_data.xml',
        'acm_agreement_contract/data/agreement_subtype_data.xml',
        'acm_agreement_contract/data/agreement_data.xml',
        'acm_agreement_contract/security/ir.model.access.csv',
        'acm_agreement_contract/wizards/agreement_create_wizards.xml',
        'acm_agreement_contract/wizards/contract_extension_wizards.xml',
        'acm_agreement_contract/wizards/contract_transfer_wizards.xml',
        'acm_agreement_contract/wizards/contract_breach_wizards.xml',
        'acm_agreement_contract/wizards/contract_terminate_wizards.xml',
        'acm_agreement_contract/wizards/contract_create_invoice_wizards.xml',
        'acm_agreement_contract/views/res_partner_views.xml',
        'acm_agreement_contract/views/res_company_views.xml',
        'acm_agreement_contract/views/product_views.xml',
        'acm_agreement_contract/views/account_analytic_account_views.xml',
        'acm_agreement_contract/views/agreement_views.xml',
        'acm_agreement_contract/report/report_templates.xml',
        'acm_agreement_contract/report/report_agreement.xml',
    ],
}
