# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class ServiceContract(models.Model):
    _name = 'service.contract'
    _description = 'Contrato de Servicio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'

    name = fields.Char(
        string='Número de Contrato',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default='Nuevo',
        tracking=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        tracking=True,
        index=True
    )
    
    start_date = fields.Date(
        string='Fecha Inicio',
        required=True,
        tracking=True
    )
    
    end_date = fields.Date(
        string='Fecha Fin',
        required=True,
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('expired', 'Expirado')
    ], string='Estado', default='draft', required=True, tracking=True)
    
    monthly_fee = fields.Float(
        string='Tarifa Mensual',
        digits='Product Price',
        tracking=True
    )
    
    total_invoiced = fields.Float(
        string='Total Facturado',
        compute='_compute_total_invoiced',
        store=True,
        digits='Product Price'
    )
    
    invoice_ids = fields.One2many(
        'account.move',
        'contract_id',
        string='Facturas',
        readonly=True
    )
    
    invoice_count = fields.Integer(
        string='Número de Facturas',
        compute='_compute_invoice_count'
    )
    
    last_invoice_date = fields.Date(
        string='Última Fecha de Facturación',
        readonly=True,
        copy=False
    )

    @api.model
    def create(self, vals):

        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('service.contract') or 'Nuevo'
        return super(ServiceContract, self).create(vals)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):

        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError(
                        'La fecha de fin debe ser mayor que la fecha de inicio.'
                    )

    @api.depends('invoice_ids', 'invoice_ids.amount_total', 'invoice_ids.state')
    def _compute_total_invoiced(self):

        for record in self:
            invoices = record.invoice_ids.filtered(
                lambda inv: inv.state == 'posted' and inv.move_type == 'out_invoice'
            )
            record.total_invoiced = sum(invoices.mapped('amount_total'))

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):

        for record in self:
            record.invoice_count = len(record.invoice_ids)

    def _update_contract_state(self):
        today = fields.Date.today()
        
        for contract in self:
            if contract.state == 'draft':
                continue
                
            if contract.end_date < today:
                contract.state = 'expired'
            elif contract.start_date <= today <= contract.end_date:
                contract.state = 'active'

    @api.model
    def _cron_update_contract_states(self):
        contracts = self.search([('state', 'in', ['active', 'draft'])])
        contracts._update_contract_state()

    def action_activate(self):

        for record in self:
            today = fields.Date.today()
            if record.start_date <= today <= record.end_date:
                record.state = 'active'
            else:
                raise ValidationError(
                    'No se puede activar el contrato. '
                    'Verifique que la fecha actual esté dentro del período del contrato.'
                )

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def generate_monthly_invoice(self):
        self.ensure_one()
        
        if self.state != 'active':
            raise ValidationError('Solo se pueden generar facturas para contratos activos.')
        
        if not self.monthly_fee:
            raise ValidationError('Debe definir una tarifa mensual para generar la factura.')
        
        today = fields.Date.today()

        if self.last_invoice_date:
            last_invoice_month = self.last_invoice_date.month
            last_invoice_year = self.last_invoice_date.year
            current_month = today.month
            current_year = today.year
            
            if last_invoice_month == current_month and last_invoice_year == current_year:
                raise ValidationError(
                    'Ya existe una factura generada para el mes actual. '
                    'No se pueden duplicar facturas.'
                )
        

        invoice_vals = {
            'partner_id': self.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_date': today,
            'contract_id': self.id,
            'invoice_line_ids': [(0, 0, {
                'name': f'Servicio de Mantenimiento - {self.name} ({today.strftime("%B %Y")})',
                'quantity': 1,
                'price_unit': self.monthly_fee,
            })]
        }
        

        invoice = self.env['account.move'].create(invoice_vals)
        

        self.last_invoice_date = today
        
        return {
            'name': 'Factura Generada',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def get_total_invoiced_by_partner(self, partner_id):
        """
        Devolver el total facturado por cliente considerando solo contratos activos.
        
        :param partner_id: ID del cliente
        :return: dict con el total facturado
        """
        contracts = self.search([
            ('partner_id', '=', partner_id),
            ('state', '=', 'active')
        ])
        
        total = sum(contracts.mapped('total_invoiced'))
        
        return {
            'partner_id': partner_id,
            'partner_name': contracts[0].partner_id.name if contracts else '',
            'active_contracts': len(contracts),
            'total_invoiced': total
        }

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'name': 'Facturas',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
            'context': {'default_contract_id': self.id}
        }


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    contract_id = fields.Many2one(
        'service.contract',
        string='Contrato de Servicio',
        readonly=True,
        copy=False
    )
