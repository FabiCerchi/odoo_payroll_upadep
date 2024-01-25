from odoo import models, api, fields

from odoo.addons.payroll.models.hr_payslip import BrowsableObject
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import logging
import math


_logger = logging.getLogger("Payslip Logger")


class HrPayslip(models.Model):
    _inherit = "hr.payslip"
    
    aplica_rd = fields.Boolean('Aplicar redondeo', default=False, help="Activa el redondeo para el basico")
    rd_amount = fields.Float('Monto RD', default=False, help="Monto a redondear")
    os_aporte_adicional = fields.Float('OS - $ Aporte Adicional', help='LSD Aporte adicional',readonly=True, default=0.0)
    os_contribucion_adicional = fields.Float('OS - $ Contribucion Adicional', help='LSD Contribucion adicional',readonly=True, default=0.0)
    ss_contrib_detraccion_promedio = fields.Float('SS - $ Detraccion Contribuciones' , help="Promedio Detraccion Contribuciones LSD", readonly=True, default=0.0)
    
    
    def max_sac_gross(self, date_from, date_to):
        '''
        Redefino el calculo del max_sac_gross para el calculo de los aguinaldos.
        Anterormente se calculaba en base al VAR_SAC_GROSS  pero al implementar nuevas estructuras
        No contemplaron que deberia estar en cada una de ellas este concepto oculto.
        
        '''
        
        employee_id = self.employee_id.id
        payslip_ids = self.env['hr.payslip'].search([('employee_id','=',employee_id),
                                                         ('state','=','done'),
                                                         ('struct_id.code','in',['AR-BASE','VAC-AR']),
                                                         ('date_from','>=', date_from),('date_to','<=',date_to)
                                                    ])
        max_sac_gross = 0
        # Diccionario para agrupar los payslips por mes
        grouped_payslips = {}
        
        for pay in payslip_ids:
            month_key = pay.date_from.strftime('%Y-%m')  # Extraer el componente del mes de la fecha
            if month_key not in grouped_payslips:
                grouped_payslips[month_key] = []
        
            grouped_payslips[month_key].append(pay)
        
        for month_key, payslip_ids in grouped_payslips.items():
            _logger.info(f"Payslips for {month_key}: {payslip_ids}")
            max_gross_parcial = 0
            
            for pay in payslip_ids:
                max_gross_parcial += pay.total_gross 
            if max_sac_gross < max_gross_parcial:
                max_sac_gross = max_gross_parcial
        
        return round(max_sac_gross,2) 
        
    def max_sac_gross_ind_ant(self, date_from, date_to):
        '''
        Redefino el calculo del max_sac_gross para el calculo de la indemnizacion por antiguedad.
        
        '''
        _logger.info('DATE FROM *************:')
        _logger.info(date_from)
        _logger.info('DATE TO *************:')
        _logger.info(date_to)
        date_from = date_from - relativedelta(months=12)
        date_from = date_from.replace(day=1, month=1)
        _logger.info('DATE FROM C *************:')
        _logger.info(date_from)
        employee_id = self.employee_id.id
        payslip_ids = self.env['hr.payslip'].search([('employee_id','=',employee_id),
                                                         ('state','=','done'),
                                                         ('struct_id.code','in',['AR-BASE','VAC-AR']),
                                                         ('date_from','>=', date_from),('date_to','<=',date_to)
                                                    ])
        max_sac_gross = 0
        # Diccionario para agrupar los payslips por mes
        grouped_payslips = {}
        
        for pay in payslip_ids:
            month_key = pay.date_from.strftime('%Y-%m')  # Extraer el componente del mes de la fecha
            if month_key not in grouped_payslips:
                grouped_payslips[month_key] = []
        
            grouped_payslips[month_key].append(pay)
        
        for month_key, payslip_ids in grouped_payslips.items():
            _logger.info(f"Payslips for {month_key}: {payslip_ids}")
            max_gross_parcial = 0
            
            for pay in payslip_ids:
                max_gross_parcial += pay.total_gross 
                for line in pay.line_ids:
                    if line.code == 'H317_AJ':
                        max_gross_parcial -= line.total
                        
            if max_sac_gross < max_gross_parcial:
                max_sac_gross = max_gross_parcial
        _logger.info(round(max_sac_gross,2))
        return round(max_sac_gross,2)              
            
    
    #Override computa el neto en regla
    def compute_sheet(self):
        dump_super = super().compute_sheet()
        for payslip in self:
            # Calcular neto del recibo
            round_line_net = payslip.line_ids.search([("code", "=", "NET"), ("slip_id", "=", payslip.id)], limit=1)
            round_line_nr = payslip.line_ids.search([("code", "=", "NR_RED"), ("slip_id", "=", payslip.id)], limit=1)
            os_aporte_adicional_line = payslip.line_ids.search([("code", "=", "H333_DIF"), ("slip_id", "=", payslip.id)], limit=1)
            os_contribucion_adicional_line = payslip.line_ids.search([("code", "=", "H402_DIF"), ("slip_id", "=", payslip.id)], limit=1)
            ss_contrib_detraccion_promedio_line = payslip.line_ids.search([("code",'=',"PROM_DETRAC"),("slip_id", "=", payslip.id)], limit=1)
            
            _logger.info('Ingreso al payslip %s ', ss_contrib_detraccion_promedio_line.total)

            payslip.os_aporte_adicional = os_aporte_adicional_line.total if os_aporte_adicional_line else 0.00
            payslip.os_contribucion_adicional = os_contribucion_adicional_line.total if os_contribucion_adicional_line else 0.00
            payslip.ss_contrib_detraccion_promedio = ss_contrib_detraccion_promedio_line.total if ss_contrib_detraccion_promedio_line else 0.00
            round_line_net.amount = round(payslip.total_net + round_line_nr.amount)
        return dump_super
        
    #Override computa embargo
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        CODE_EMBARGO = 'EMB_JUD'
        if self.contract_id.embargo_judicial > 0:
            for rec in self.line_ids:
                if rec.code == CODE_EMBARGO:
                    self.contract_id.embargo_judicial+= rec.total
                    break
        return res

    #Override cancela el embargo
    def action_payslip_cancel(self):
        CODE_EMBARGO = 'EMB_JUD'
        if self.state == 'done':
            for rec in self.line_ids:
                if rec.code == CODE_EMBARGO:
                    _logger.info(str(rec.total))
                    self.contract_id.embargo_judicial-= rec.total
                    break
        res = super(HrPayslip, self).action_payslip_cancel()
        return res 
        
    #Override para SAC_PROP
    def get_sac_worked_days(self, date_to):
        res = super(HrPayslip, self).get_sac_worked_days(date_to)
        #Licencias que restan de la base SAC
        leave_days = 0      
        if not date_to:
            date_to = datetime.now()
        if date_to.month >= 7:
            date_from = datetime(date_to.year, 7, 1)
        if date_to.month <= 6:
            date_from = datetime(date_to.year, 1, 1)
        
        payslips_done = self.env['hr.payslip'].search([('date_from','>=',date_from),('date_to','<=',date_to),('employee_id','=',self.employee_id.id)], limit=6)
        for payslip in payslips_done:
            leave_days+= payslip.number_of_leaves_lp()
            
        res+= leave_days
        return max(res, 0)
    
    @api.model
    def get_pvar(self, contract, date_from):
        period_limit = date_from - relativedelta(months=6)
        employee_payslip = self.env['hr.payslip'].search([('employee_id','=', contract.employee_id.id),('date_from','>=',period_limit),('date_from','<',date_from),('state','=','done')])
        C_VM = 0.0
        _logger.info(str(employee_payslip))
        for payslip in employee_payslip:
            _logger.info('--------------------')
            _logger.info(str(payslip.name))
            lines = payslip.line_ids
            for line in lines:
                if line.code == 'C_VM':
                    _logger.info(str(line.total))
                    C_VM+= line.total
                    break
        #Aguilera Javier.
        return C_VM/6
    
    @api.model
    def get_category_value_price_by_code_and_date(self, code , date_from):
        '''
        param code- str : codigo de categoria a buscar
        param date_from - date: fecha del precio a buscar de la cat anterior.
        
        proposito: Funcion creada para LP. Se utiliza para traer los valores de la categoria indicada por el codigo en una fecha especifica 
        en caso de no encontrar la fecha especifica retornara el ultimo valor de la categoria anterior o igual a la fecha.
        
        No se valida la existencia del codigo de la categoria ya que lo manejamos nosotros.
        
        A tener en cuenta: todas los precios de las categorias comienzan con 1/mes/anio
        
        '''        
        labor_union_cat_id = self.env['hr.labor_union.category'].search([('code','=',code)],limit = 1).id
        cat_price = self.env['hr.labor_union.category.price'].search([('labor_union_category_id','=',labor_union_cat_id),('from_date','=',date_from)],limit = 1)
        if not cat_price:
            cat_price = self.env['hr.labor_union.category.price'].search([('labor_union_category_id','=',labor_union_cat_id),('from_date','<',date_from)],limit = 1)
        return cat_price.value
    
    @api.model
    def number_of_leaves_lp(self):
        self.ensure_one()
        LEAVES = ['H122','H126','H132','H133','H125','H110','H108','H109','H132']
        for rec in self:
            sum = 0.0
            leave_ids = [x for x in rec.worked_days_line_ids if x.code in LEAVES]
            if leave_ids:
                for leave in leave_ids:
                    sum+= leave.number_of_days
            return sum
                
