from odoo import models, api, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    afiliado_upsra = fields.Boolean('Afiliado a UPSRA?', default=False)
    embargo_judicial = fields.Float('Embargo Judicial', default=False)
    aporta_ft = fields.Boolean('Aporte Obra Social FT', default=False, help='Fuerza el aporte OS')
    TIPOS_DESPIDO = [
        ('sin_causa', 'Sin Causa'),
        ('fuerza_mayor', 'Fuerza Mayor'),
        ('fallecimiento', 'Fallecimiento'),
    ]
    tipo_despido = fields.Selection(TIPOS_DESPIDO, string='Tipo de Despido', default=False)