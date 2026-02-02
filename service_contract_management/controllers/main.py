# -*- coding: utf-8 -*-

import json
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class ServiceContractAPI(http.Controller):
    
    @http.route(
        '/api/contracts/active',
        type='http',
        auth='user',
        methods=['GET'],
        csrf=False
    )
    def get_active_contracts(self, **kwargs):
        """
        Endpoint REST para consultar contratos activos por partner_id.
        
        Parámetros:
            partner_id: ID del cliente (requerido)
        
        Ejemplo de uso:
            GET /api/contracts/active?partner_id=123
        
        Respuesta JSON:
            {
                "success": true,
                "data": [
                    {
                        "id": 1,
                        "name": "CTR/00001",
                        "partner_id": 123,
                        "partner_name": "Cliente Ejemplo",
                        "start_date": "2024-01-01",
                        "end_date": "2024-12-31",
                        "monthly_fee": 500.00,
                        "total_invoiced": 2500.00,
                        "state": "active"
                    }
                ],
                "count": 1
            }
        """
        try:
            # Validar parámetro partner_id
            partner_id = kwargs.get('partner_id')
            
            if not partner_id:
                return self._error_response(
                    'El parámetro partner_id es requerido',
                    400
                )
            
            try:
                partner_id = int(partner_id)
            except ValueError:
                return self._error_response(
                    'El parámetro partner_id debe ser un número entero',
                    400
                )
            
            # Verificar que el partner existe
            partner = request.env['res.partner'].sudo().browse(partner_id)
            if not partner.exists():
                return self._error_response(
                    f'No se encontró el cliente con ID {partner_id}',
                    404
                )
            
            # Buscar contratos activos
            contracts = request.env['service.contract'].sudo().search([
                ('partner_id', '=', partner_id),
                ('state', '=', 'active')
            ])
            
            # Preparar datos de respuesta
            contract_data = []
            for contract in contracts:
                contract_data.append({
                    'id': contract.id,
                    'name': contract.name,
                    'partner_id': contract.partner_id.id,
                    'partner_name': contract.partner_id.name,
                    'start_date': contract.start_date.strftime('%Y-%m-%d') if contract.start_date else None,
                    'end_date': contract.end_date.strftime('%Y-%m-%d') if contract.end_date else None,
                    'monthly_fee': contract.monthly_fee,
                    'total_invoiced': contract.total_invoiced,
                    'state': contract.state,
                    'invoice_count': contract.invoice_count
                })
            
            return self._success_response(contract_data, len(contracts))
            
        except Exception as e:
            _logger.error(f"Error en API de contratos: {str(e)}", exc_info=True)
            return self._error_response(
                'Error interno del servidor',
                500
            )

    @http.route(
        '/api/contracts/<int:contract_id>',
        type='http',
        auth='user',
        methods=['GET'],
        csrf=False
    )
    def get_contract_detail(self, contract_id, **kwargs):
        """
        Endpoint REST para obtener detalle de un contrato específico.
        
        Parámetros:
            contract_id: ID del contrato (en la URL)
        
        Ejemplo de uso:
            GET /api/contracts/1
        """
        try:
            contract = request.env['service.contract'].sudo().browse(contract_id)
            
            if not contract.exists():
                return self._error_response(
                    f'No se encontró el contrato con ID {contract_id}',
                    404
                )
            
            # Preparar datos detallados
            contract_data = {
                'id': contract.id,
                'name': contract.name,
                'partner_id': contract.partner_id.id,
                'partner_name': contract.partner_id.name,
                'start_date': contract.start_date.strftime('%Y-%m-%d') if contract.start_date else None,
                'end_date': contract.end_date.strftime('%Y-%m-%d') if contract.end_date else None,
                'monthly_fee': contract.monthly_fee,
                'total_invoiced': contract.total_invoiced,
                'state': contract.state,
                'invoice_count': contract.invoice_count,
                'last_invoice_date': contract.last_invoice_date.strftime('%Y-%m-%d') if contract.last_invoice_date else None,
                'invoices': [
                    {
                        'id': inv.id,
                        'name': inv.name,
                        'date': inv.invoice_date.strftime('%Y-%m-%d') if inv.invoice_date else None,
                        'amount': inv.amount_total,
                        'state': inv.state
                    } for inv in contract.invoice_ids
                ]
            }
            
            return self._success_response(contract_data)
            
        except Exception as e:
            _logger.error(f"Error en API de contratos: {str(e)}", exc_info=True)
            return self._error_response(
                'Error interno del servidor',
                500
            )

    @http.route(
        '/api/contracts/stats',
        type='http',
        auth='user',
        methods=['GET'],
        csrf=False
    )
    def get_contract_stats(self, **kwargs):
        """
        Endpoint REST para obtener estadísticas generales de contratos.
        
        Ejemplo de uso:
            GET /api/contracts/stats
        """
        try:
            Contract = request.env['service.contract'].sudo()
            
            total_contracts = Contract.search_count([])
            active_contracts = Contract.search_count([('state', '=', 'active')])
            draft_contracts = Contract.search_count([('state', '=', 'draft')])
            expired_contracts = Contract.search_count([('state', '=', 'expired')])
            
            # Calcular totales
            active_contract_objs = Contract.search([('state', '=', 'active')])
            total_monthly_fees = sum(active_contract_objs.mapped('monthly_fee'))
            total_invoiced = sum(active_contract_objs.mapped('total_invoiced'))
            
            stats = {
                'total_contracts': total_contracts,
                'active_contracts': active_contracts,
                'draft_contracts': draft_contracts,
                'expired_contracts': expired_contracts,
                'total_monthly_fees': total_monthly_fees,
                'total_invoiced': total_invoiced
            }
            
            return self._success_response(stats)
            
        except Exception as e:
            _logger.error(f"Error en API de estadísticas: {str(e)}", exc_info=True)
            return self._error_response(
                'Error interno del servidor',
                500
            )

    def _success_response(self, data, count=None):
        """Generar respuesta exitosa en formato JSON"""
        response_data = {
            'success': True,
            'data': data
        }
        
        if count is not None:
            response_data['count'] = count
        
        return Response(
            json.dumps(response_data, default=str),
            content_type='application/json',
            status=200
        )

    def _error_response(self, message, status_code):
        """Generar respuesta de error en formato JSON"""
        response_data = {
            'success': False,
            'error': message
        }
        
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=status_code
        )
