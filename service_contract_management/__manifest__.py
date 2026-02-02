# -*- coding: utf-8 -*-
{
    'name': 'Service Contract Management',
    'version': '17.0.1.0.0',
    'category': 'Services',
    'summary': 'Gestión de contratos de mantenimiento y facturación',
    'description': """
        Módulo para gestionar contratos de servicio con:
        - Gestión de contratos de mantenimiento
        - Facturación mensual automática
        - Reportes PDF
        - API REST para consultas
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/service_contract_views.xml',
        'reports/service_contract_report.xml',
        'reports/service_contract_report_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
