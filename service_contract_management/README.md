# Service Contract Management - Módulo Odoo 17+

Módulo para gestión de contratos de mantenimiento y facturación básica asociada.

## Características Principales

### Modelo service.contract
- **Campos principales:**
  - `name`: Número de contrato (generado automáticamente)
  - `partner_id`: Cliente (Many2one res.partner)
  - `start_date`: Fecha de inicio
  - `end_date`: Fecha de fin
  - `state`: Estado (draft, active, expired)
  - `monthly_fee`: Tarifa mensual
  - `total_invoiced`: Total facturado (campo computado)

### Lógica de Negocio Implementada

1. **Validación de fechas**: La fecha de fin debe ser mayor que la fecha de inicio
2. **Actualización automática de estados**: 
   - Cron job diario que actualiza estados según fecha actual
   - Método `_update_contract_state()` para actualización manual
3. **Generación de facturas mensuales**:
   - Método `generate_monthly_invoice()` que previene duplicados
   - Verifica que no exista factura para el mes actual
   - Actualiza campo `last_invoice_date`
4. **Total facturado por cliente**:
   - Método `get_total_invoiced_by_partner()` 
   - Considera solo contratos activos
   - Retorna información detallada del cliente

### Vistas Implementadas

1. **Vista Tree**: Lista de contratos con decoración por estado
2. **Vista Form**: Formulario completo con:
   - Statusbar (draft → active → expired)
   - Botones de acción (Activar, Generar Factura, Ver Facturas)
   - Stat button para contar facturas
   - Notebook con pestaña de facturas
   - Chatter para seguimiento
3. **Vista Search**: Filtros y agrupaciones por:
   - Estado (draft, active, expired)
   - Fechas (inicio/fin este mes)
   - Agrupación por fecha, cliente, estado

### Reporte QWeb

Reporte PDF que incluye:
- Número de contrato
- Datos del cliente (nombre, RUC/CI)
- Período del contrato
- Estado actual
- Tarifa mensual
- Total facturado
- Lista de facturas generadas

### API REST

Tres endpoints implementados:

#### 1. Consultar contratos activos por cliente
```
GET /api/contracts/active?partner_id=123
```

**Respuesta:**
```json
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
            "state": "active",
            "invoice_count": 5
        }
    ],
    "count": 1
}
```

#### 2. Obtener detalle de un contrato
```
GET /api/contracts/1
```

**Respuesta:** Incluye datos del contrato y lista completa de facturas

#### 3. Estadísticas generales
```
GET /api/contracts/stats
```

**Respuesta:** Totales de contratos por estado, tarifas mensuales y facturación total

### Características Adicionales

- **Secuencia automática**: Genera números de contrato tipo CTR/00001
- **Cron job**: Actualización diaria automática de estados
- **Herencia mail.thread**: Seguimiento completo con chatter
- **Validaciones robustas**: Control de duplicados y validaciones de negocio
- **Manejo de errores**: API REST con respuestas estructuradas
- **Campo computado**: total_invoiced se calcula automáticamente desde facturas validadas

## Instalación

1. Copiar el módulo a la carpeta de addons de Odoo:
```bash
cp -r service_contract_management /path/to/odoo/addons/
```

2. Actualizar lista de aplicaciones en Odoo:
   - Activar modo desarrollador
   - Ir a Aplicaciones
   - Click en "Actualizar lista de aplicaciones"

3. Buscar e instalar "Service Contract Management"

## Dependencias

- `base`: Módulo base de Odoo
- `account`: Módulo de contabilidad (para facturas)

## Uso Básico

### Crear un contrato

1. Ir a menú "Contratos de Servicio" → "Contratos"
2. Click en "Crear"
3. Llenar campos requeridos:
   - Cliente
   - Fechas de inicio y fin
   - Tarifa mensual
4. Click en "Activar" para cambiar estado a activo

### Generar facturas

1. Abrir un contrato en estado "Activo"
2. Click en botón "Generar Factura Mensual"
3. Se creará una factura por el valor de monthly_fee
4. El sistema previene crear facturas duplicadas del mismo mes

### Ver reportes

1. Seleccionar uno o varios contratos
2. Click en "Imprimir" → "Reporte de Contrato"
3. Se generará un PDF con toda la información

### Usar API REST

Autenticación: Se requiere usuario de Odoo con sesión activa

**Ejemplo con curl:**
```bash
# Login primero y obtener session_id
curl -X POST http://localhost:8069/web/session/authenticate \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","params":{"db":"tu_base_datos","login":"admin","password":"admin"}}'

# Consultar contratos activos
curl -X GET "http://localhost:8069/api/contracts/active?partner_id=7" \
  --cookie "session_id=TU_SESSION_ID"
```

## Estructura del Módulo

```
service_contract_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── service_contract.py
├── views/
│   └── service_contract_views.xml
├── reports/
│   ├── service_contract_report.xml
│   └── service_contract_report_template.xml
├── controllers/
│   ├── __init__.py
│   └── main.py
├── security/
│   └── ir.model.access.csv
└── README.md
```

## Notas Técnicas

- Compatible con Odoo 17+
- Usa ORM estándar de Odoo
- Implementa best practices de desarrollo Odoo
- Código documentado en español
- Manejo robusto de errores en API
- Prevención de duplicados en facturación

## Autor

Desarrollado como prueba técnica para demostrar conocimientos en:
- Desarrollo de módulos Odoo
- Lógica de negocio compleja
- Vistas y UX
- Reportes QWeb
- APIs REST
- Validaciones y constraints

## Licencia

LGPL-3
