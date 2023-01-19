# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'ACM :: Agreement Contract Template',
    'version': '12.0.1.0.0',
    'author': 'Ecosoft, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Agreement',
    'depends': [
        'agreement_legal',
    ],
    'data': [
        "data/agreement_data.xml",
        "data/agreement_sections_data.xml",
        "data/agreement_clauses_data.xml",
        "data/agreement_appendices_data.xml",
    ]
}
