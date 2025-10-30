# Fuentes de Información y Aprendizajes - AgentTracker

## 📊 Las 4 Fuentes de Datos Principales

**Ubicación**: `/Users/alfil/Desktop/Desarrollos/Comsulting/Fuentes de informacion/`

### 1. **Historial 2024-2025.xlsx** (Fuente principal de horas)
**Ubicación**: `/Users/alfil/Desktop/Desarrollos/Comsulting/Historial 2024-2025.xlsx`

**Descripción**: Exportación de Harvest (sistema de time tracking)

**Hojas**:
- `TD 2024`: Tabla dinámica de horas 2024 por cliente/área/mes
- `TD 2025`: Tabla dinámica de horas 2025 por cliente/área/mes
- `Horas`: Datos crudos - 105,501 registros totales

**Estructura de hoja "Horas"**:
```
Columnas principales:
- Date: Fecha del registro
- Client: Nombre del cliente (ej: CLÍNICAS, EBM, Falabella)
- Project: Nombre del proyecto
- Area: Área de trabajo (ej: Com. Externas, Diseño Editorial, RRSS)
- Task: Tarea específica
- Hours: Horas trabajadas
- First Name / Last Name: Nombre de la persona
- Cost Amount: Costo en pesos chilenos
```

**Datos 2025** (Jan-Sep):
- Total registros: 45,750
- Total horas: 40,426.83
- 25 clientes únicos
- Personas: ~38 personas diferentes

**Clientes en Excel 2025**:
1. AFP Modelo - 921.32 horas
2. CLÍNICAS - 4,508.55 horas (se mapea a "EBM" en BD)
3. Capstone Copper - 3,293.44 horas
4. Collahuasi - 4,817.93 horas
5. Comité de Paltas - 906.37 horas
6. Comsulting Gestión Interna - 4,838.61 horas
7. DH - 327.21 horas
8. EBM - 658.29 horas (cliente separado de CLÍNICAS)
9. EMBAJADA ITALIA - 148.82 horas
10. EMPRESAS COPEC - 3,118.57 horas
11. FALABELLA - 5,386.91 horas
12. Frutas de Chile - 3,464.45 horas
13. GUACOLDA - 1,864.54 horas
14. HITES - 809.28 horas
15. HSE - Capston Copper - 188.67 horas
16. IQ SALMONES - 729.93 horas
17. ISAPRES - 1,414.56 horas
18. LARRAÍN VIAL - 256.41 horas
19. LIBERTY - 45.86 horas
20. MAE - 1,150.00 horas
21. MINI HIDROS - 168.70 horas
22. NOVA AUSTRAL - 632.44 horas
23. OXZO - 354.79 horas
24. SONNEDIX - 93.72 horas
25. Santander - 327.46 horas

**Áreas en Excel 2025**:
- Asuntos públicos
- Com. Externas
- Com. Internas
- Diseño Editorial
- Desarrollo Web
- Monitoreo
- RRSS

### 2. **Cliente_Comsulting.xlsx** (Ingresos facturados por cliente)

**Descripción**: Detalle de clientes permanentes y spot con sus servicios y tarifas mensuales

**Hojas**:
- `Cliente_Comsulting`: Resumen general
- `Permanentes`: Clientes con contratos permanentes (67 filas, 30 columnas)
- `Spot`: Clientes por proyecto

**Estructura de hoja "Permanentes"**:
```
Columnas:
- CLIENTES PERMANENTES: Nombre del cliente
- Area: Área de servicio (Externas, Internas, RRSS, etc.)
- Servicio: Descripción del servicio
- 2024-01 a 2024-12: Ingresos mensuales en UF
- 2025-01 a 2025-09: Ingresos mensuales en UF 2025
```

**Clientes principales en "Permanentes"**:
- AFP MODELO: Asesoría Comunicacional UF 225/mes
- EBM:
  - Asesoría Comunicacional UF 856/mes
  - Digital UF 210/mes
  - Isapres UF 55/mes
  - Monitoreo Sindicatos UF 14/mes
  - Talleres de vocería UF 13.2/mes (promedio)
  - News Letter UF 9/mes
  - **TOTAL EBM**: ~1,157 UF/mes
- COLLAHUASI: ~803 UF/mes (varios servicios)
- FALABELLA: 610 UF/mes
- Etc.

**Hoja "Facturación"**:
- Detalle de servicios específicos por cliente
- Fee mensual total por cliente
- Notas sobre cambios de tarifa

**IMPORTANTE**: Esta es la fuente de INGRESOS REALES facturados

### 3. **Costos RRHH_Facturacion 09_2025 VF.xlsx** (Costos de personal)

**Descripción**: Planilla de costos de recursos humanos y facturación actualizada a Septiembre 2025

**Hojas**:
- `Costos`: Detalle de haberes, bonos y costo total mensual por persona (43 filas = 37 personas activas)
- `Facturación`: Resumen de ingresos por cliente y servicio

**Estructura de hoja "Costos"**:
```
Columnas:
- Nombre: Nombre del empleado
- Total haberes 09-2025: Sueldo bruto septiembre 2025
- Bono cliente: Bonos específicos por cliente
- Bono turnos fines de semana
- Seguro complementario
- Bono sala cuna
- Haberes (neto de bonos)
- Bono N° sueldos: Cantidad de sueldos de bono anual
- Bono anual /12: Bono mensualizado
- Costo total mensual empresa: COSTO REAL MENSUAL
- Fecha de ingreso 2025: Si entró durante 2025
```

**Personal clave y costos mensuales** (Septiembre 2025):
1. Blanca Bulnes: 7,419,495 pesos
2. Macarena Puiggrredon: 7,419,494 pesos
3. Bernardita Ochagavia: 6,550,324 pesos (incluye bono anual)
4. Carolina Romero: 6,471,115 pesos
5. Nicolás Marticorena: 6,931,883 pesos (incluye bono cliente)
...
37. Hernán Díaz: 1,793,767 pesos (ingreso 2025-08-01)

**Personal nuevo 2025** (con fecha de ingreso):
- Nidia Millahueique: 2025-08-04
- Luisa Mendoza: 2025-10-01
- Victor Guillou: 2025-06-16
- Anais Sarmiento: 2025-03-18
- Sofía Martínez: 2025-07-01
- Christian Orrego: 2025-07-17
- Francisca Carlino: 2025-07-24
- Hernán Díaz: 2025-08-01

**IMPORTANTE**: Esta es la fuente de COSTOS REALES de personal. Los costos varían mes a mes por entradas/salidas.

### 4. **Planilla Flujo de Caja Comsulting 2025.xlsx** (Flujo de caja proyectado)

**Descripción**: Planilla de flujo de caja con proyecciones financieras

**Hojas principales**:
- `2025`: Flujo de caja mensual 2025
- `BBDD CLIENTES`: Base de datos de clientes
- `escala de sueldos`: Escala salarial
- Otras hojas históricas (2019, 2020, etc.)

**Hoja "2025"**:
- Ingresos proyectados por mes
- Gastos proyectados por mes
- Flujo de caja neto
- Provisiones y reservas

**IMPORTANTE**: Esta es la fuente de PROYECCIONES y PRESUPUESTO

---

## 📊 Comparación entre Fuentes

### Ingresos por Cliente

**Fuente 1**: `Historial 2024-2025.xlsx` → HORAS trabajadas (no ingresos)
**Fuente 2**: `Cliente_Comsulting.xlsx` → INGRESOS facturados mensuales
**Fuente 3**: `Costos RRHH_Facturacion 09_2025 VF.xlsx` → También tiene hoja de facturación
**Fuente 4**: `Planilla Flujo de Caja` → Ingresos proyectados

**Discrepancia clave**:
- El dashboard muestra "Ingresos año: 53,793.8 UF"
- Esto viene de la tabla `ingresos_mensuales` en la BD
- **PERO** necesitamos verificar si coincide con `Cliente_Comsulting.xlsx`

### Costos de Personal

**Fuente 3**: `Costos RRHH_Facturacion 09_2025 VF.xlsx`
- **37 personas activas** en Septiembre 2025
- Costo total mensual: ~120-130 millones de pesos (estimado)
- **Conversión a UF** (38,000 pesos/UF): ~3,150-3,420 UF/mes

**Dashboard actual**:
- Muestra "Costos año: 28,751.2 UF"
- **Cálculo**: `costo_mensual_total_uf * mes_actual` (línea 776 de app.py)
- Si divide: 28,751.2 / 10 meses = 2,875 UF/mes
- **Discrepancia**: Falta ~300-500 UF/mes

**Problema identificado**:
- El dashboard calcula costos multiplicando costo mensual actual × 10
- NO considera entradas/salidas de personal (8 personas entraron en 2025)
- Debería sumar los costos REALES de cada mes

### Overhead

**Problema**: El overhead incluye "gap de horas no imputadas"

**Ejemplo**: Si una persona tiene:
- 156 horas disponibles/mes
- 100 horas registradas
- 56 horas de gap
- Costo: 20 UF/hora
- **Gap costo**: 56 × 20 = 1,120 UF

Este costo de 1,120 UF se distribuye a TODOS los clientes proporcionalmente. Esto infla el overhead artificialmente.

**Solución propuesta**:
- Opción A: Quitar el gap del overhead
- Opción B: Solo distribuir gastos operacionales (tabla `gastos_overhead`)
- Opción C: Mejorar el tracking de horas para reducir el gap

---

### 5. **Base de Datos PostgreSQL (Producción en Render)**

**Conexión**:
```
DATABASE_URL="postgresql://agenttracker_db_user:SVoi2QQ0qt0Zye0QPzEj7g2lX9RJ2ANb@dpg-d3pb2i3ipnbc739ps5r0-a/agenttracker_db"
```

**Tablas principales**:
- `personas`: Empleados de Comsulting
- `clientes`: Clientes de Comsulting
- `areas`: Áreas de negocio
- `servicios`: Servicios/proyectos por área
- `tareas`: Tareas específicas dentro de servicios
- `registros_horas`: Registro de horas trabajadas (relación persona-cliente-área-servicio-tarea)
- `ingresos_mensuales`: Ingresos facturados por cliente/mes (vía ServicioCliente)
- `gastos_overhead`: Gastos operacionales mensuales

**Áreas en BD Producción** (diferentes del Excel):
- Asuntos Públicos
- Comunicaciones (área general, default)
- Diseño
- Externas
- Internas
- Redes Sociales

**Clientes en BD Producción**:
- Incluye ~30+ clientes activos
- Nombres pueden diferir de Excel (mayúsculas/minúsculas)
- Ejemplos: EBM, Falabella, Embajada de Italia, Empresas Copec

### 3. **Archivos de Configuración**

**app.py** (Aplicación principal Flask)
- Líneas 127-250: `calcular_overhead_distribuido()` - Calcula overhead y distribuye por cliente
- Líneas 730-802: `dashboard()` - Dashboard principal con stats de empresa
- Líneas 2388-2459: `api_top_clientes_rentables()` - API que calcula rentabilidad por cliente

**Constantes importantes**:
```python
HORAS_EFECTIVAS_MES = 156  # Horas mensuales full-time
VALOR_UF_ACTUAL = 38000    # Pesos chilenos por UF
```

---

## 🔍 Aprendizajes Clave

### 1. **Mapeo de Nombres de Personas** (Excel → BD)

**Problema**: Harvest usa nombres diferentes que la BD de AgentTracker

**Solución**: Mapeo manual en `importar_horas_produccion.py`

```python
MAPEO_NOMBRES = {
    'Ángeles Pérez': 'María De Los Ángeles Pérez',
    'Andrés Azócar': 'Raúl Andrés Azócar',
    'Nidia Millahueique': 'Juana Nidia Millahueique',
    'Bernardita Ochagavía': 'María Bernardita Ochagavia',
    'Ignacio Echevería': 'Luis Ignacio Echeverría',
    'Ignacio Díaz': 'Ignacio Diaz',
    'Liliana Cortés': 'Liliana Cortes',
    'Sofía Martinez': 'Sofía Martínez',
    'Víctor Guillou': 'Victor Guillou',
    'Hernan Díaz Diseño': 'Hernán Díaz',
    'Nicolás Campos': 'Nicolás Campos',
}
```

**Personas creadas durante importación** (no existían en BD):
- María Marañón
- Vicente Vera
- Catalina Durán
- Javiera Flores
- Felipe Iglesias
- Rosirene Clavero
- Belén Castro
- Nicolás Campos

### 2. **Mapeo de Nombres de Clientes** (Excel → BD)

```python
MAPEO_CLIENTES = {
    'CLÍNICAS': 'EBM',  # Mismo cliente, diferente nombre en Harvest
    'FALABELLA': 'Falabella',  # Case difference
    'EMBAJADA ITALIA': 'Embajada de Italia',  # Case difference
}
```

**IMPORTANTE**: CLÍNICAS (4,508 horas) + EBM (658 horas) = 5,166 horas totales para cliente "EBM" en BD

### 3. **Mapeo de Áreas** (Excel → BD)

**Función**: `mapear_area_excel_a_bd()` en `importar_horas_produccion.py`

```python
Mapeo:
- "externa" → "Externas"
- "interna" → "Internas"
- "asuntos públicos" → "Asuntos Públicos"
- "rrss" / "social" / "redes" → "Redes Sociales"
- "diseño" / "design" → "Diseño"
- "comunicacion" → "Comunicaciones"
- Default → "Comunicaciones"
```

### 4. **Estructura de Datos en BD**

**Jerarquía**:
```
Cliente
  └─ Servicio (Proyecto)
       └─ Área
            └─ Tarea

Ejemplo:
EBM
  └─ Com. Externas
       └─ Comunicaciones
            └─ Estrategia comunicacional
```

**Registro de Horas**:
```sql
registros_horas:
  - persona_id (quién trabajó)
  - cliente_id (para qué cliente)
  - area_id (en qué área)
  - servicio_id (en qué proyecto)
  - tarea_id (qué tarea específica)
  - fecha
  - horas
  - descripcion
```

### 5. **Secuencias de PostgreSQL**

**Problema descubierto**: Las secuencias auto-incrementales estaban desincronizadas

**Error**:
```
duplicate key value violates unique constraint "servicios_pkey"
Key (id)=(27) already exists
```

**Causa**:
- Existen servicios con ID 27, 28, etc.
- La secuencia `servicios_id_seq` estaba en 19
- Al insertar nuevo servicio, PostgreSQL intentaba usar ID=19 (ya existe)

**Solución**: Función `arreglar_secuencias()` que sincroniza todas las secuencias

```python
def arreglar_secuencias(conn):
    tablas_con_secuencia = [
        ('personas', 'personas_id_seq'),
        ('clientes', 'clientes_id_seq'),
        ('areas', 'areas_id_seq'),
        ('servicios', 'servicios_id_seq'),
        ('tareas', 'tareas_id_seq'),
        ('registros_horas', 'registros_horas_id_seq'),
    ]

    for tabla, secuencia in tablas_con_secuencia:
        conn.execute(text(f"""
            SELECT setval('{secuencia}', (SELECT COALESCE(MAX(id), 1) FROM {tabla}), true)
        """))
```

### 6. **Transacciones PostgreSQL y Rollback**

**Problema descubierto**: Cuando ocurría un error SQL, la transacción quedaba abortada

**Error**:
```
(psycopg2.errors.InFailedSqlTransaction) current transaction is aborted,
commands ignored until end of transaction block
```

**Causa**: El script no hacía `rollback()` después de errores

**Solución**: Agregar `conn.rollback()` en el bloque except

```python
try:
    # ... operaciones SQL ...
except Exception as e:
    conn.rollback()  # ← CRÍTICO
    registros_error += 1
    continue
```

### 7. **Resultado de Importación**

**Última importación exitosa** (2025-10-29):
```
Total registros en Excel (2025):     45,750
Importados nuevos:                    9,448
Duplicados (ya existían):            36,302
Con errores:                              0

Total registros en BD (2025):        43,798
Total horas en BD (2025):         39,279.26

Objetivo (Excel):                    45,750 registros
Objetivo (Excel):                 40,426.83 horas

Diferencia horas:                 -1,147.57 (-2.8%)
```

**Diferencia de -2.8%** es aceptable - puede deberse a:
- Personas sin mapeo (~1,950 registros)
- Registros con horas = 0 (saltados)
- Registros sin cliente (saltados)

---

## 🔴 Problemas Pendientes de Rentabilidad

### Problema 1: Cálculo de Costos Anuales en Dashboard

**Archivo**: `app.py`, líneas 775-776

**Código actual**:
```python
# Costos del año (costo mensual × meses transcurridos)
costo_año_uf = costo_mensual_total_uf * mes_actual  # mes_actual = 10
```

**Problema**:
- Multiplica el costo mensual de personas activas HOY por 10 meses
- No considera entradas/salidas de personal durante el año
- Ingresos son de TODO el año, pero costos solo de 10 meses

**Resultado**:
- Dashboard muestra: Ingresos año: 53,793.8 UF
- Dashboard muestra: Costos año: 28,751.2 UF
- **PERO** costos reales deberían ser ~41,107 UF (según tabla de clientes)

### Problema 2: Overhead Incluye "Gap de Horas No Imputadas"

**Archivo**: `app.py`, líneas 187-199 en `calcular_overhead_distribuido()`

**Código actual**:
```python
for mes_iter in meses_a_calcular:
    horas_disponibles_mes = calcular_horas_disponibles_mes(año, mes_iter)

    for persona in personas_activas:
        horas_registradas = horas_por_persona_mes.get(persona.id, {}).get(mes_iter, 0)
        horas_gap = max(0, horas_disponibles_mes - horas_registradas)

        if horas_gap > 0:
            costo_horas_no_imputadas_uf += horas_gap * persona.costo_hora_uf
```

**Problema**:
- Si una persona tiene 156 horas disponibles pero solo registró 100 horas
- Las 56 horas de "gap" se cobran como overhead
- Este overhead se distribuye proporcionalmente a TODOS los clientes

**Resultado**:
- **EBM**: Costo variable 1,505 UF, overhead 4,708 UF (3.1x el costo directo)
- **Capstone**: Costo variable 1,574 UF, overhead 2,972 UF (1.9x el costo directo)
- Overhead total inflado artificialmente

### Problema 3: Rentabilidades Absurdas

**Ejemplos**:
- **LIBERTY**: 79% margen (300 UF ingresos, 63 UF costo total)
  - Costo variable: 20.7 UF (muy bajo)
  - Overhead: 42.5 UF
  - Si tiene pocas horas, recibe poco overhead proporcional

- **Embajada de Italia**: -146% margen
  - Ingresos: 88.8 UF
  - Costos directos: 80.8 UF
  - Overhead: 137.8 UF (mayor que los ingresos!)

- **Internas**: 100% margen (5,450 UF ingresos, 0 UF costos)
  - Posible causa: Horas de "Comsulting Gestión Interna" no se asignan a cliente específico

- **Diseño**: 100% margen (2,926 UF ingresos, 0.9 UF costos)
  - Solo 0.5 horas registradas
  - Posible causa: Horas de diseño registradas en otros clientes

---

## 📁 Archivos de Scripts de Importación

### `importar_horas_produccion.py`
**Propósito**: Importar horas desde Excel a PostgreSQL (producción)

**Funciones principales**:
1. `arreglar_secuencias()` - Sincroniza secuencias PostgreSQL
2. `crear_personas_faltantes()` - Crea 8 personas nuevas
3. `obtener_mapeo_personas()` - Mapea nombres Excel → IDs BD
4. `mapear_area_excel_a_bd()` - Mapea áreas Excel → BD
5. `obtener_o_crear_cliente()` - Busca/crea cliente (case-insensitive)
6. `importar_registros()` - Loop principal de importación

**Flujo**:
1. Arregla secuencias
2. Crea personas faltantes
3. Lee Excel (hoja "Horas")
4. Filtra 2025 (Jan-Sep)
5. Para cada registro:
   - Mapea nombre persona → ID
   - Mapea nombre cliente → ID (crea si no existe)
   - Mapea área → ID (crea si no existe)
   - Crea servicio/tarea si no existen
   - Verifica duplicados
   - Inserta registro de horas
6. Muestra resumen

### `arreglar_secuencias.py`
**Propósito**: Script standalone para arreglar secuencias PostgreSQL

**Uso**:
```bash
export DATABASE_URL="postgresql://..."
python3 arreglar_secuencias.py
```

### `diagnostico_render.py`
**Propósito**: Diagnóstico completo de BD en producción

**Muestra**:
- Estructura de tablas y columnas
- Clientes existentes
- Personas activas
- Registros de horas (2025)
- Verificación de clientes del Excel
- Áreas existentes

### `verificar_datos_produccion.py`
**Propósito**: Verificación rápida de datos post-importación

**Muestra**:
- Total registros/horas 2025
- Top 10 clientes por horas
- Top 10 personas por horas
- Verificación de personas nuevas

---

## 🚀 Comandos Útiles en Render Shell

```bash
# Configurar DATABASE_URL
export DATABASE_URL="postgresql://agenttracker_db_user:SVoi2QQ0qt0Zye0QPzEj7g2lX9RJ2ANb@dpg-d3pb2i3ipnbc739ps5r0-a/agenttracker_db"

# Instalar dependencias
pip3 install pandas openpyxl sqlalchemy psycopg2-binary

# Arreglar secuencias (opcional, el script principal lo hace automáticamente)
python3 arreglar_secuencias.py

# Ejecutar importación
python3 importar_horas_produccion.py

# Verificar resultados
python3 verificar_datos_produccion.py

# Diagnóstico completo
python3 diagnostico_render.py
```

---

## 📝 Notas Importantes

1. **No confundir clientes**: CLÍNICAS (Excel) → EBM (BD), pero EBM también existe como cliente separado en Excel
2. **Áreas tienen nombres diferentes**: "Com. Externas" (Excel) vs "Externas" (BD)
3. **Case-insensitive search**: Siempre usar `UPPER()` al buscar clientes/áreas
4. **Secuencias**: Ejecutar `arreglar_secuencias()` ANTES de cualquier importación
5. **Rollback**: SIEMPRE hacer rollback en errores SQL para evitar transacciones abortadas
6. **Horas efectivas**: 156 horas/mes (Mon-Thu: 9h, Fri: 8h)
7. **UF actual**: 38,000 pesos chilenos (hardcodeado, debería actualizarse periódicamente)

---

**Última actualización**: 2025-10-29
**Autor**: Claude Code (con supervisión de Alfil)
