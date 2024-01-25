{
    'name': 'Soporte Sindicato UPADEP CASA (Argentina)',
    'version': '14.0.3.0.0',
    'description': 'Datos y adecuaciones para soportar el sindicato UPADEP CASA en la localizacion Argentina de Payroll.',
    'summary': 'Agrega conceptos, categorias y precios para el sindicato UPADEP CASA.',
    'author': 'Fabian Cerchi, Exemax',
    'website': '',
    'license': 'LGPL-3',
    'category': 'Payroll',
    'depends': [
        'l10n_ar_payroll_lu_upadep',
    ],
    'data': [
        'data/lu_upadep_casa_categories_prices.xml',
        'data/lu_upadep_casa_salary_parameter.xml',
        'data/lu_upadep_casa_salary_rules.xml',
        'data/lu_upadep_casa_advantage.xml',
        'data/lu_upadep_casa_salary_structures.xml',
        'data/lu_upadep_casa_overtimes_rules.xml',
        'data/lu_upadep_casa_overtimes_types.xml',


    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
