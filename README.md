# Service Contract Management

Módulo Odoo 17+ para gestión de contratos de mantenimiento y facturación.


1. En Odoo:
   - Activar modo desarrollador
   - Ir a **Aplicaciones** → **Actualizar lista de aplicaciones**
   - Buscar "Service Contract Management"
   - Instalar

## Uso Básico

### Crear Contrato
1. **Menú:** Contratos de Servicio → Contratos
2. **Crear** y llenar:
   - Cliente
   - Fecha inicio y fin
   - Tarifa mensual
3. Click **Activar**

### Generar Factura
1. Abrir contrato activo
2. Click **Generar Factura Mensual**
3. La factura se crea automáticamente

### Generar Reporte PDF
1. Seleccionar contrato
2. **Imprimir** → **Reporte de Contrato**


```
service_contract_management/
├── models/
│   └── service_contract.py      # Modelo principal
├── views/
│   └── service_contract_views.xml
├── reports/
│   ├── service_contract_report.xml
│   └── service_contract_report_template.xml
├── controllers/
│   └── main.py                  # API REST
└── security/
    └── ir.model.access.csv
```
