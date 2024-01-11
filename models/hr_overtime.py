from odoo import models, api, _
#from odoo.addons.payroll.models.hr_payslip import BrowsableObject
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger("Overtime logger")

class HrOvertime(models.Model):
    _inherit = 'hr.overtime'
    
    #Override
    '''
    def action_approve(self):
        _logger.info('Ingreso al action')
        for rec in self:
            if rec.overtime_type_duration_type == 'hour':
                if rec.overtime_hours<= 0:
                    raise ValidationError(_("No es posible aprobar ya que el valor de las horas es 0.0 " + str(rec.name)))
    '''
                    