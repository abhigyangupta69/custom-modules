# -*- coding: utf-8 -*-
{
    'name': 'verts_v11_saledemo',
    'version': '1.0',
    "sequence": 1,
    'complexity': "",
    'category': 'Generic Modules/Others',
    'description': """


    """,
    'author': '',
    'website': '',
    'depends': ["base",'sale'],
    'data': [
        "views/sale_demo_view.xml",
        "views/menu_view.xml",
        'data/ir_sequence_data.xml',
        'report/saledemo_report.xml',
        'report/saledemo_report_template.xml',

    ],
    'installable': True,
    'auto_install': False,
}
