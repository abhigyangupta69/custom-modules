{
    'name' : 'Compliance Human Resource',
    'version' : '1.1',
    'author' : 'Anshul Bhardwaj',
    'category' : 'Extend Hr Functionality',
    'description' : """
    This module Extend the functionality of HR module according to the rules define by Govt. of India and Respected authority.
""",
    'website': 'https://www.openerp4you.in',
    'depends' : ['base','hr','hr_attendance','hr_holidays'],
    'data': [
             'security/security_view.xml',
             'security/ir.model.access.csv',
             'view/hr_employee_view.xml',
             'view/hr_employee_other_view.xml',
             'view/holiday_view.xml',
             'wizard/wiz_employee_compliance_view.xml',
             'report/hr_compliance_report.xml',
             'view/report_temp_view.xml',
             'report/employee_qweb_view.xml',
             'view/hr_header_layout_view.xml',
             'view/attendance_synchronize_view.xml',
             'wizard/wiz_attendance_scheduler_view.xml',
             'view/report_salary_report_view.xml',
             'report/salary_register_report_view.xml',
             'wizard/wiz_salary_report_view.xml',
             'report/salary_report_view.xml',             
             'wizard/wiz_salary_view.xml',
             'view/salary_payment_view.xml',
             'view/loan_deduction_view.xml',   
             'wizard/wiz_update_ot_view.xml',
             'wizard/wiz_create_attendance_view.xml',
             'wizard/wiz_performance_register_view.xml',
             'wizard/wiz_ot_register_view.xml',
             'wizard/wiz_daily_performance_view.xml',
             'report/daily_performance_register_report_view.xml',
             'view/report_daily_performance_register_view.xml',
             'wizard/wiz_employee_card_view.xml',
             'report/employee_icard_view.xml',
             'view/report_employee_icard_view.xml',
             'wizard/wiz_leave_register_view.xml',
             'view/report_leave_register_view.xml',
             'report/leave_register_view.xml',
             'view/report_master_report_view.xml',
			 'wizard/wiz_employee_bonus_report_view.xml',
             'wizard/wiz_employee_pf_form_view.xml',
             'view/report_temp_pf_form.xml',
             'wizard/wiz_form12_register_view.xml',
             'view/form12_register_template_view.xml',
             'report/form12_register_view.xml',
             'view/report_trans_promo_view.xml',
             'wizard/wiz_employee_pf_upload_report_view.xml',
             'wizard/wiz_employee_salary_deduction_view.xml',
             'wizard/wiz_earn_leave_report_view.xml',
             'view/report_form15G_view.xml',
             'view/report_emp_salary_certificate_view.xml',
             'view/report_emp_leave_app_view.xml',
             'wizard/wiz_neem_trainee_stipend_register_view.xml',
    ],
    'demo':[],
    'installable': True,
    'auto_install': False,
}
