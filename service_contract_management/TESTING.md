# Ejemplos de Uso y Casos de Prueba

## Casos de Prueba - Modelo y Lógica

### 1. Crear contrato en borrador
```python
# En shell de Odoo
contract = env['service.contract'].create({
    'partner_id': 7,  # Reemplazar con ID de partner válido
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    'monthly_fee': 500.00
})
# Verificar: contract.name debe ser algo como 'CTR/00001'
# Verificar: contract.state debe ser 'draft'
```

### 2. Validar fechas (debe fallar)
```python
# Intentar crear contrato con fecha fin menor a fecha inicio
try:
    contract = env['service.contract'].create({
        'partner_id': 7,
        'start_date': '2024-12-31',
        'end_date': '2024-01-01',  # Fecha inválida
        'monthly_fee': 500.00
    })
except Exception as e:
    print("Error esperado:", e)
# Debe lanzar ValidationError: "La fecha de fin debe ser mayor que la fecha de inicio"
```

### 3. Activar contrato
```python
contract = env['service.contract'].browse(1)  # ID del contrato creado
contract.action_activate()
# Verificar: contract.state debe cambiar a 'active'
```

### 4. Generar factura mensual
```python
contract = env['service.contract'].search([('state', '=', 'active')], limit=1)
result = contract.generate_monthly_invoice()
# Verificar: Se debe crear una factura
# Verificar: contract.last_invoice_date debe actualizarse
# Verificar: contract.total_invoiced debe incrementarse (después de validar factura)
```

### 5. Prevenir duplicación de facturas (debe fallar)
```python
contract = env['service.contract'].browse(1)
contract.generate_monthly_invoice()  # Primera vez - OK
try:
    contract.generate_monthly_invoice()  # Segunda vez mismo mes - debe fallar
except Exception as e:
    print("Error esperado:", e)
# Debe lanzar ValidationError: "Ya existe una factura generada para el mes actual"
```

### 6. Validar factura y verificar total_invoiced
```python
contract = env['service.contract'].browse(1)
# Generar y validar factura
invoice = contract.invoice_ids[-1]  # Última factura
invoice.action_post()  # Validar factura
contract._compute_total_invoiced()  # Forzar recálculo
# Verificar: contract.total_invoiced debe ser igual a la suma de facturas validadas
```

### 7. Obtener total facturado por cliente
```python
partner_id = 7  # ID del cliente
result = env['service.contract'].get_total_invoiced_by_partner(partner_id)
print(result)
# Debe retornar:
# {
#     'partner_id': 7,
#     'partner_name': 'Nombre del Cliente',
#     'active_contracts': 2,
#     'total_invoiced': 5000.00
# }
```

### 8. Actualizar estados automáticamente
```python
# Crear contrato expirado
old_contract = env['service.contract'].create({
    'partner_id': 7,
    'start_date': '2023-01-01',
    'end_date': '2023-12-31',
    'monthly_fee': 500.00,
    'state': 'active'
})
# Ejecutar actualización de estados
env['service.contract']._cron_update_contract_states()
old_contract.refresh()
# Verificar: old_contract.state debe cambiar a 'expired'
```

## Casos de Prueba - API REST

### 1. Consultar contratos activos por cliente

**Usando curl:**
```bash
# Primero autenticarse
curl -X POST http://localhost:8069/web/session/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "params": {
      "db": "tu_base_datos",
      "login": "admin",
      "password": "admin"
    }
  }'

# Guardar el session_id de la respuesta

# Consultar contratos activos
curl -X GET "http://localhost:8069/api/contracts/active?partner_id=7" \
  --cookie "session_id=TU_SESSION_ID"
```

**Usando Python:**
```python
import requests
import json

base_url = "http://localhost:8069"
db = "tu_base_datos"
username = "admin"
password = "admin"

# Login
session = requests.Session()
login_data = {
    "jsonrpc": "2.0",
    "params": {
        "db": db,
        "login": username,
        "password": password
    }
}
response = session.post(f"{base_url}/web/session/authenticate", json=login_data)

# Consultar contratos activos
partner_id = 7
response = session.get(f"{base_url}/api/contracts/active?partner_id={partner_id}")
print(json.dumps(response.json(), indent=2))
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "CTR/00001",
      "partner_id": 7,
      "partner_name": "Azure Interior",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "monthly_fee": 500.0,
      "total_invoiced": 2500.0,
      "state": "active",
      "invoice_count": 5
    }
  ],
  "count": 1
}
```

### 2. Error: partner_id no proporcionado
```bash
curl -X GET "http://localhost:8069/api/contracts/active" \
  --cookie "session_id=TU_SESSION_ID"
```

**Respuesta esperada:**
```json
{
  "success": false,
  "error": "El parámetro partner_id es requerido"
}
```

### 3. Error: partner_id inválido
```bash
curl -X GET "http://localhost:8069/api/contracts/active?partner_id=abc" \
  --cookie "session_id=TU_SESSION_ID"
```

**Respuesta esperada:**
```json
{
  "success": false,
  "error": "El parámetro partner_id debe ser un número entero"
}
```

### 4. Error: Cliente no existe
```bash
curl -X GET "http://localhost:8069/api/contracts/active?partner_id=99999" \
  --cookie "session_id=TU_SESSION_ID"
```

**Respuesta esperada:**
```json
{
  "success": false,
  "error": "No se encontró el cliente con ID 99999"
}
```

### 5. Obtener detalle de un contrato
```bash
curl -X GET "http://localhost:8069/api/contracts/1" \
  --cookie "session_id=TU_SESSION_ID"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "CTR/00001",
    "partner_id": 7,
    "partner_name": "Azure Interior",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "monthly_fee": 500.0,
    "total_invoiced": 2500.0,
    "state": "active",
    "invoice_count": 5,
    "last_invoice_date": "2024-05-01",
    "invoices": [
      {
        "id": 10,
        "name": "INV/2024/00001",
        "date": "2024-01-01",
        "amount": 500.0,
        "state": "posted"
      }
    ]
  }
}
```

### 6. Obtener estadísticas generales
```bash
curl -X GET "http://localhost:8069/api/contracts/stats" \
  --cookie "session_id=TU_SESSION_ID"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "total_contracts": 15,
    "active_contracts": 8,
    "draft_contracts": 3,
    "expired_contracts": 4,
    "total_monthly_fees": 4000.0,
    "total_invoiced": 20000.0
  }
}
```

## Casos de Prueba - Vistas

### 1. Vista Tree
- Abrir menú "Contratos de Servicio" → "Contratos"
- Verificar que se muestran todos los campos
- Verificar decoración de colores:
  - Verde para contratos activos
  - Rojo para contratos expirados
  - Gris para borradores

### 2. Vista Form
- Crear nuevo contrato
- Verificar statusbar (draft → active → expired)
- Verificar que botón "Activar" solo aparece en estado draft
- Verificar que botón "Generar Factura" solo aparece en estado active
- Verificar stat button de facturas
- Verificar notebook con pestaña de facturas
- Verificar chatter funcional

### 3. Vista Search
- Aplicar filtro "Activos" - debe mostrar solo contratos activos
- Aplicar filtro "Inicio Este Mes" - debe filtrar por fecha de inicio
- Aplicar agrupación por "Cliente" - debe agrupar correctamente
- Buscar por número de contrato - debe funcionar búsqueda

## Casos de Prueba - Reporte

### 1. Generar reporte PDF
- Seleccionar un contrato con facturas
- Click en "Imprimir" → "Reporte de Contrato"
- Verificar que PDF contiene:
  - Número de contrato
  - Datos del cliente (nombre, RUC/CI si existe)
  - Período del contrato (fechas)
  - Estado con badge de color
  - Tarifa mensual formateada como moneda
  - Total facturado
  - Tabla de facturas generadas
  - Fecha de generación del reporte

### 2. Reporte sin facturas
- Seleccionar un contrato nuevo sin facturas
- Generar reporte
- Verificar que no muestra tabla de facturas vacía

## Script de Prueba Completo

```python
# Ejecutar en shell de Odoo: odoo-bin shell -d tu_base_datos

# 1. Crear partner de prueba
partner = env['res.partner'].create({
    'name': 'Cliente de Prueba',
    'vat': '1234567890001',
    'email': 'cliente@ejemplo.com'
})

# 2. Crear contrato
contract = env['service.contract'].create({
    'partner_id': partner.id,
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    'monthly_fee': 500.00
})

print(f"Contrato creado: {contract.name}")
print(f"Estado inicial: {contract.state}")

# 3. Activar contrato
contract.action_activate()
print(f"Estado después de activar: {contract.state}")

# 4. Generar facturas
for i in range(3):
    try:
        contract.generate_monthly_invoice()
        print(f"Factura {i+1} generada")
        # Simular cambio de mes modificando last_invoice_date
        if i < 2:
            contract.last_invoice_date = contract.last_invoice_date - relativedelta(months=1)
    except Exception as e:
        print(f"Error: {e}")

# 5. Validar facturas
for invoice in contract.invoice_ids:
    invoice.action_post()
    print(f"Factura {invoice.name} validada")

# 6. Verificar total facturado
print(f"Total facturado: {contract.total_invoiced}")
print(f"Número de facturas: {contract.invoice_count}")

# 7. Consultar total por cliente
result = env['service.contract'].get_total_invoiced_by_partner(partner.id)
print("Resultado por cliente:", result)

# 8. Generar reporte
contract.env.ref('service_contract_management.action_report_service_contract').report_action(contract)

print("¡Todas las pruebas completadas!")
```

## Checklist de Validación

- [ ] Secuencia de contratos funciona (CTR/00001, CTR/00002, etc.)
- [ ] Validación de fechas funciona correctamente
- [ ] Estado se actualiza automáticamente con cron
- [ ] No se pueden duplicar facturas del mismo mes
- [ ] Total facturado se calcula correctamente
- [ ] Método get_total_invoiced_by_partner retorna datos correctos
- [ ] Vista tree muestra todos los campos
- [ ] Vista form tiene statusbar funcional
- [ ] Botones de acción aparecen según estado
- [ ] Filtros de búsqueda funcionan
- [ ] Reporte PDF genera correctamente
- [ ] API REST /active retorna contratos activos
- [ ] API REST valida parámetros correctamente
- [ ] API REST maneja errores apropiadamente
- [ ] Chatter funciona (seguimiento de cambios)
- [ ] Stat button de facturas funciona
