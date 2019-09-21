{
    'name': 'Hospital Management',
    'version': '1.0',
    'category': 'Hospital',
    'summary': 'patients,facilities ',
    'description': """ This module is related to patients and hospital facilities. """,

    'website': '',
    'depends': [],
    'data': [
            'wizard/wiz_image_hospital_view.xml',
            'wizard/wiz_hospital_management_view.xml',
            'views/hospital_management_view.xml',
            'report/hospital_management_report.xml',
            'report/hospital_management_report_template.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
