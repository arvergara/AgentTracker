# Sistema de Administración Comsulting

Sistema completo de gestión administrativa para reemplazar y mejorar Harvest. Gestiona horas, facturación, costos de equipo, indicadores de productividad, rentabilidad de clientes y valorización de proyectos.

## 🚀 Características Principales

### 1. Capacidad Disponible del Equipo
- ✅ Visualización de capacidad disponible por persona
- ✅ Identificación de personas sobrecargadas (>100% utilización)
- ✅ Reportes históricos (1, 3, 6 meses, medio año)
- ✅ Alertas automáticas para personas sin registrar horas (últimos 2 días)
- ✅ Calculadora de necesidad de contratación

### 2. Rentabilidad
- ✅ Rentabilidad por cliente (6 meses, 1 año)
- ✅ Cálculo de márgenes (bruto y neto)
- ✅ Aportes en UF, pesos y % de facturación
- ✅ Rankings de clientes más rentables
- ✅ Rentabilidad por área de Comsulting
- ✅ Análisis de crecimiento año a año

### 3. Pricing de Proyectos
- ✅ Cálculo automático de precios basado en horas requeridas
- ✅ Ajuste de margen deseado (antes y después de impuestos)
- ✅ Valorización en UF actualizada
- ✅ Desglose detallado por cargo
- ✅ Consideración de costos por hora

### 4. Reporte de Productividad
- ✅ Análisis individual por persona con **prorrateo inteligente**
- ✅ ROI por empleado y por proyecto
- ✅ Distribución de costos e ingresos proporcional
- ✅ Recomendaciones automáticas de aumentos de sueldo
- ✅ Cálculo graduado de bonos (100%, 75%, 50%, 25%, 0%)
- ✅ Métricas avanzadas: Eficiencia de costos, Productividad por hora, Margen porcentual

#### 📊 Metodología de Productividad

El sistema utiliza un **modelo de prorrateo inteligente**:

1. **Costos**: Se asignan directamente según horas trabajadas × costo/hora
2. **Ingresos**: Se prorratean según % de participación en costos del proyecto
3. **Métricas calculadas**:
   - **ROI Global**: (Ingresos - Costos) / Costos × 100
   - **Eficiencia**: Ingresos / Costos (cuánto genera por cada UF invertida)
   - **Productividad/Hora**: Ingresos totales / Horas trabajadas
   - **Margen Porcentual**: (Margen / Ingresos) × 100

**Ejemplo**:
- Juan trabaja 40h en Cliente A (costo: 80 UF)
- Cliente A tiene costos totales de 200 UF
- Juan representa 40% de los costos del Cliente A
- Si Cliente A facturó 300 UF, Juan recibe crédito por 120 UF (40% de 300)
- Margen de Juan = 120 - 80 = 40 UF
- ROI de Juan en Cliente A = 50%

Ver documentación completa en: `METODOLOGIA_PRODUCTIVIDAD.md`

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd /home/claude
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt --break-system-packages
```

### 3. Inicializar la base de datos

La aplicación usa SQLite, por lo que no necesita configuración adicional de base de datos.

## ▶️ Ejecutar la Aplicación

### 1. Iniciar el servidor

```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

### 2. Inicializar datos de prueba (primera vez)

Accede a: `http://localhost:5000/inicializar-datos`

Esto creará:
- 6 personas de ejemplo
- 4 clientes de ejemplo
- 90 días de registros de horas
- Facturas de ejemplo
- Valor UF actual

## 📱 Uso de la Aplicación

### Dashboard Principal
Accede al dashboard en: `/dashboard`

Aquí encontrarás:
- **Capacidad del Equipo**: Visualización en tiempo real con estados (disponible/óptimo/sobrecargado)
- **Alertas**: Personas que no han registrado horas
- **Calculadora de Contratación**: Determina si necesitas contratar basado en nuevos proyectos
- **Top 5 Clientes**: Ranking de clientes más rentables
- **Rentabilidad por Área**: Análisis de todas las áreas de negocio
- **Calculadora de Pricing**: Calcula precios para nuevos proyectos

### Gestión de Personas
`/personas`

- Ver listado de todo el equipo
- Agregar nuevas personas
- Filtrar por área, cargo, tipo de jornada
- Ver reportes de productividad individual

### Gestión de Clientes
`/clientes`

- Ver listado de clientes activos
- Agregar nuevos clientes (permanentes o spot)
- Filtrar por tipo y área
- Analizar rentabilidad (6 meses o 1 año)

### Registro de Horas
`/horas`

- Registrar horas trabajadas
- Ver histórico de registros
- Filtrar por fecha y persona
- Sistema simple y rápido de registro

## 🔍 API Endpoints

La aplicación incluye varios endpoints de API para integraciones:

### Capacidad
```
GET /api/capacidad/<meses>
```
Retorna la capacidad del equipo para el período especificado.

### Personas sin Horas
```
GET /api/sin-horas
```
Lista personas que no han registrado horas en los últimos 2 días.

### Necesidad de Contratación
```
POST /api/necesidad-contratacion
Body: {
    "horas_socio": 20,
    "horas_director": 40,
    "horas_consultor": 80,
    "area": "Externas"
}
```

### Rentabilidad por Cliente
```
GET /api/rentabilidad/cliente/<cliente_id>/<meses>
```

### Ranking de Rentabilidad
```
GET /api/rentabilidad/ranking?year=2025&top=10
```

### Rentabilidad por Área
```
GET /api/rentabilidad/areas
```

### Pricing de Proyectos
```
POST /api/pricing
Body: {
    "horas_por_cargo": {
        "Socio": 20,
        "Director": 40,
        "Consultor": 80
    },
    "margen_deseado": 12.5
}
```

### Productividad Individual
```
GET /api/productividad/<persona_id>/<meses>
```

## 📊 Configuración

### Constantes importantes (en app.py):

```python
HORAS_EFECTIVAS_MES = 156  # Horas efectivas mensuales para full-time
IMPUESTO = 0.27  # 27% de impuestos en Chile
```

### Áreas de negocio:
- Externas
- Internas
- Asuntos Públicos
- Redes sociales
- Diseño

### Tipos de jornada:
- Full-time (156 horas/mes)
- Media jornada (78 horas/mes)

### Tipos de clientes:
- Permanente
- Spot

## 🏗️ Estructura del Proyecto

```
/home/claude/
├── app.py                    # Aplicación principal Flask
├── requirements.txt          # Dependencias Python
├── templates/               # Plantillas HTML
│   ├── base.html           # Template base
│   ├── index.html          # Página de inicio
│   ├── dashboard.html      # Dashboard principal
│   ├── personas.html       # Listado de personas
│   ├── persona_form.html   # Formulario de personas
│   ├── clientes.html       # Listado de clientes
│   ├── cliente_form.html   # Formulario de clientes
│   ├── horas.html          # Registro de horas
│   └── hora_form.html      # Formulario de horas
├── static/
│   ├── css/
│   │   └── style.css       # Estilos CSS
│   └── js/
│       └── main.js         # JavaScript utilities
└── comsulting.db           # Base de datos SQLite (se crea automáticamente)
```

## 🗃️ Modelo de Datos

### Persona
- Nombre, email, cargo
- Tipo de jornada (full-time/media-jornada)
- Área de trabajo
- Costo por hora (UF)
- Sueldo mensual (UF)

### Cliente
- Nombre
- Tipo (permanente/spot)
- Área
- Fecha de inicio

### Registro de Horas
- Persona
- Cliente
- Fecha
- Horas trabajadas
- Descripción

### Factura
- Cliente
- Número de factura
- Fecha
- Monto en UF
- Estado (pagada/no pagada)

### Valor UF
- Fecha
- Valor en pesos chilenos

## 💡 Casos de Uso

### 1. Ver capacidad disponible del equipo
1. Ir a Dashboard
2. La sección "Capacidad Disponible del Equipo" muestra automáticamente el último mes
3. Usar los botones para ver 1, 3 o 6 meses
4. Los cards se colorean según estado (verde=disponible, azul=óptimo, rojo=sobrecargado)

### 2. Determinar si necesitas contratar
1. Ir a Dashboard
2. En "Calculadora de Necesidad de Contratación"
3. Ingresar horas requeridas por cargo para nuevo cliente
4. Seleccionar área (opcional)
5. Click en "Calcular"
6. El sistema indica si necesitas contratar y qué cargo

### 3. Analizar rentabilidad de un cliente
1. Ir a "Clientes"
2. Buscar el cliente
3. Click en "6 Meses" o "1 Año"
4. Ver análisis completo con:
   - Ingresos y costos en UF y pesos
   - Utilidad bruta y neta
   - Margen de rentabilidad

### 4. Calcular precio para nuevo proyecto
1. Ir a Dashboard
2. En "Calculadora de Pricing de Proyectos"
3. Ingresar horas requeridas por cargo
4. Ajustar margen deseado
5. Click en "Calcular Precio"
6. Ver precio en UF y pesos con desglose completo

### 5. Evaluar productividad de una persona
1. Ir a "Personas"
2. Buscar la persona
3. Click en "📊 Productividad"
4. Ver reporte con:
   - Horas trabajadas vs esperadas
   - ROI individual
   - Recomendaciones de aumentos y bonos

## 🔐 Seguridad

**Nota**: Esta es una versión de desarrollo. Para producción se recomienda:
- Implementar autenticación de usuarios
- Usar una base de datos más robusta (PostgreSQL, MySQL)
- Configurar HTTPS
- Implementar respaldos automáticos
- Agregar validación de permisos por rol

## 🐛 Troubleshooting

### Error: "No module named flask"
```bash
pip install -r requirements.txt --break-system-packages
```

### Error: "Database is locked"
Cierra todas las instancias de la aplicación y vuelve a iniciar.

### Los datos de prueba no se cargan
Accede directamente a: `http://localhost:5000/inicializar-datos`

### El valor de la UF no se actualiza
El sistema usa un valor por defecto. Para producción, integrar con API del Banco Central de Chile.

## 📈 Mejoras Futuras

- [ ] Integración con API del Banco Central para UF en tiempo real
- [ ] Exportación de reportes a PDF y Excel
- [ ] Gráficos interactivos con Chart.js
- [ ] Sistema de notificaciones por email
- [ ] Módulo de facturación automatizada
- [ ] Dashboard ejecutivo con KPIs
- [ ] App móvil para registro de horas
- [ ] Integración con Google Calendar
- [ ] Sistema de aprobación de horas
- [ ] Reportes personalizables

## 🔬 Análisis Avanzado de Productividad

El sistema incluye un script de análisis avanzado (`analisis_productividad.py`) que proporciona:

### Funcionalidades del Script

#### 1. **Análisis Comparativo del Equipo**
```python
python analisis_productividad.py
```

Genera reportes ejecutivos con:
- Ranking de personas por ROI
- Promedios del equipo (ROI, margen, eficiencia, cumplimiento)
- Top 5 performers
- Personas que necesitan atención

#### 2. **Análisis por Área**
Métricas agregadas por área de negocio:
- ROI promedio del área
- Margen e ingresos totales
- Eficiencia comparada entre áreas
- Distribución de recursos

#### 3. **Identificación de Desbalances**
Detecta automáticamente:
- 🔴 **Sobrecargados**: >110% utilización
- 🟡 **Subutilizados**: <70% utilización  
- 🟢 **Óptimo**: 70-110% utilización

#### 4. **Proyección de Bonos**
Calcula el presupuesto necesario para bonos anuales basado en:
- Desempeño actual del equipo
- Criterios graduados (100%, 75%, 50%, 25%, 0%)
- Total proyectado en UF
- Distribución por nivel

#### 5. **Reporte Ejecutivo Completo**
Un reporte integral para presentar a dirección con:
- Métricas globales de la empresa
- Análisis detallado del equipo
- Comparativa por áreas
- Balance de carga de trabajo
- Proyecciones financieras

### Uso del Script

```bash
# Generar reporte en consola
python analisis_productividad.py

# Generar reporte JSON
# Modificar última línea para usar: generar_reporte_json()
```

### Ejemplo de Salida

```
================================================================================
            REPORTE EJECUTIVO DE PRODUCTIVIDAD - COMSULTING
================================================================================

📅 Período: 6 meses
📅 Fecha: 2025-09-30 22:45

--------------------------------------------------------------------------------
                     MÉTRICAS GLOBALES DE LA EMPRESA
--------------------------------------------------------------------------------

💼 Horas Totales:          5040.00 h
💰 Costos Totales:          600.50 UF
💵 Ingresos Totales:        900.75 UF
📊 Margen Total:            300.25 UF (33.3%)
📈 ROI Empresa:              50.04 %

--------------------------------------------------------------------------------
                          ANÁLISIS DEL EQUIPO
--------------------------------------------------------------------------------

👥 Total Personas:       6

📊 Promedios del Equipo:
   ROI Promedio:             45.20 %
   Margen Promedio:          28.50 %
   Eficiencia Promedio:       1.45 x
   Cumplimiento Promedio:    92.30 %

🏆 Top 5 Performers:
   1. María González         ROI:  65.5%  Margen: 32.1%
   2. Juan Pérez            ROI:  52.3%  Margen: 29.8%
   3. Ana Martínez          ROI:  48.7%  Margen: 27.5%
   ...
```

## 👥 Soporte

Para soporte o consultas sobre el sistema, contacta al equipo de desarrollo.

## 📄 Licencia

Sistema desarrollado para Comsulting - 2025

---

**Desarrollado con ❤️ para optimizar la gestión de Comsulting**
