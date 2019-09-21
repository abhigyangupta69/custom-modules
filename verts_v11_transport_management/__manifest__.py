# -*- coding: utf-8 -*-
{
    'name': 'verts_v11_transport_management',
    'version': '1.0',
    "sequence": 1,
    'complexity': "",
    'category': '',
    'description': """


    """,
    'author': '',
    'website': '',
    'depends': ["base",'product','sale'],
    'data': [
        "views/ir_sequence_data.xml",
        "views/charge_view.xml",
        "views/charges_type_view.xml",
        "views/executor_reasons_view.xml",
        "views/fuel_price_list_view.xml",
        "views/fuel_types_view.xml",
        "views/location_types_view.xml",
        "views/material_status_view.xml",
        "views/odc_reasons_view.xml",
        "views/request_priority_view.xml",
        "views/requests_view.xml",
        "views/vehicle_brands_view.xml",
        "views/vehicle_models_view.xml",
        "views/vehicle_request_checklist_view.xml",
        "views/vehicle_type_view.xml",
        "wizard/vehicle_report_view.xml",
        "wizard/sale_wizard_report_view.xml",
        "wizard/wiz_request_view.xml",
        "report/transport_management_report.xml",
        "report/transport_management_report_template.xml",
        "views/menu_view.xml",
        "views/request_execution_view.xml",
        "data/data_view.xml",
        "security/sale_order_security.xml",


    ],
    'installable': True,
    'auto_install': False,
}
