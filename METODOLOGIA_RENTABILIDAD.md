# Metodología Correcta de Cálculo de Rentabilidad - AgentTracker

**Última actualización**: 2025-10-30
**Autor**: Alfil + Claude Code

---

## 📋 Principio Fundamental

> **La rentabilidad debe ser LA MISMA al subdividirla por área o por cliente**

Esto significa que:
- Rentabilidad Total Empresa = Suma de Rentabilidad por Cliente = Suma de Rentabilidad por Área
- Ingresos Total - Costos Total = Margen Total
- Este margen debe cuadrar independiente de cómo se agrupe (por cliente o por área)

---

## 📊 Las 4 Fuentes de Información (en orden de flujo)

### 1. **Planilla Flujo de Caja Comsulting 2025.xlsx** → Ingresos y Gastos Mensuales Totales

**Ubicación**: `/Users/alfil/Desktop/Desarrollos/Comsulting/Fuentes de informacion/Planilla Flujo de Caja Comsulting 2025.xlsx`

**Hoja**: `2025`

**Qué contiene**:
- **Fila 173**: Total Ingresos mes (UF por mes)
  ```
  Enero: 6,224.25 UF → 209,607,828 pesos
  Febrero: 201,353,380 pesos
  Marzo: 201,376,082 pesos
  ... hasta Septiembre
  ```

- **Fila 119**: Total Gastos mes
  ```
  Incluye:
  - Sueldos y aportes patronales
  - Arriendo oficinas (UF 123 + UF 116.7)
  - Suscripciones (Litoralpress, Talkwalker, etc.)
  - Servicios externalizados (contador, aseo, soporte)
  - Gastos operacionales
  ```

**IMPORTANTE**: Esta es la fuente oficial de ingresos y gastos mensuales totales.

---

### 2. **Historial 2024-2025.xlsx** → Horas por Persona, Cliente y Área

**Ubicación**: `/Users/alfil/Desktop/Desarrollos/Comsulting/Historial 2024-2025.xlsx`

**Hoja**: `Horas`

**Qué contiene**:
- 105,501 registros totales
- 45,750 registros 2025 (Ene-Sep)
- 40,426.83 horas totales 2025

**Estructura**:
```
Cada registro tiene:
- Date: Fecha
- Client: Cliente (ej: EBM, Falabella, Collahuasi)
- Area: Área (ej: Com. Externas, Diseño Editorial, RRSS)
- Task: Tarea específica
- Hours: Horas trabajadas
- First Name / Last Name: Persona que trabajó
- Cost Amount: Costo en pesos
```

**Qué se calcula**:
- **Horas por Cliente**: Suma de horas trabajadas para cada cliente
- **Horas por Área**: Suma de horas trabajadas en cada área
- **Horas por Persona**: Total de horas registradas por cada empleado
- **Horas NO asignadas**: Gap = Horas disponibles - Horas registradas

---

### 3. **Facturación por área 2025 v2.xlsx** → Subdivisión de Ingresos por Cliente y Área

**Ubicación**: `/Users/alfil/Desktop/Desarrollos/Comsulting/Fuentes de informacion/Facturación por área 2025 v2.xlsx`

**Hojas**:
1. `Costos`: Idéntico a "Costos RRHH_Facturacion 09_2025 VF.xlsx"
2. `Facturación`: Detalle de servicios por cliente
3. `Facturacion_cliente_area`: **Tabla clave** que mapea ingresos por cliente y área

**Hoja `Facturacion_cliente_area`** (LA MÁS IMPORTANTE):

```
| Área                      | Cliente Permanente | UF/mes | Cliente Spot        | UF/mes | Total Anual |
|---------------------------|--------------------|--------|---------------------|--------|-------------|
| Comunicaciones externas   | EBM                | 881.2  | BCI                 | 53.0   |             |
|                          | Collahuasi         | 350.0  | Capital Advisors    | 20.8   |             |
|                          | AFP Modelo         | 225.0  | Capstone            | 16.7   |             |
|                          | Empresas Copec     | 200.0  | Concha y Toro       | 19.5   |             |
|                          | Grupo Falabella    | 510.0  | Embajada Italia     | 22.2   |             |
|                          | Frutas de Chile    | 250.0  | Falabella           | 16.7   |             |
|                          | Guacolda           | 50.0   | Oxzo                | 17.5   |             |
|                          | Hites              | 150.0  |                     |        |             |
|                          | Isidoro Quiroga    | 254.0  |                     |        |             |
|                          | MAE                | 120.0  |                     |        |             |
|                          | Mantos Cooper      | 100.0  |                     |        |             |
|                          | Manto Verde        | 100.0  |                     |        |             |
|                          | Nova Austral       | 115.0  |                     |        |             |
|                          | Oxzo               | 33.3   |                     |        |             |
|                          | Sonnedix           | 40.0   |                     |        |             |
|                          | LarrainVial        | 30.0   |                     |        |             |
|                          | Liberty seguros    | 30.0   |                     |        |             |
|                          | **Subtotal**       | 3438.5 |                     | 166.4  | 41,428.4    |
| AAPP                      | Frutas de Chile    | 100.0  |                     |        |             |
|                          | Guacolda           | 100.0  |                     |        |             |
| ... etc                   |                    |        |                     |        |             |
```

**IMPORTANTE**: Esta tabla permite asignar ingresos específicos a cada combinación Cliente + Área.

---

### 4. **Cliente_Comsulting.xlsx** → Confirmación y Detalle de Ingresos

**Ubicación**: `/Users/alfil/Desktop/Desarrollos/Comsulting/Fuentes de informacion/Cliente_Comsulting.xlsx`

**Hoja**: `Permanentes`

**Qué contiene**:
- Detalle mes a mes de ingresos por cliente
- Sirve para **confirmar** los datos de Facturación por área
- Incluye columnas de Ene-2024 a Sep-2025

**Ejemplo** (Cliente EBM):
```
CLIENTES PERMANENTES | Area      | Servicio                     | 2025-01 | 2025-02 | ... | 2025-09
---------------------|-----------|------------------------------|---------|---------|-----|--------
EBM                  | Externas  | Asesoría Comunicacional     | 856     | 856     | ... | 856
EBM                  | RRSS      | Digital                     | 210     | 210     | ... | 210
EBM                  | Externas  | Isapres                     | 55      | 55      | ... | 55
EBM                  | Interna   | Monitoreo Sindicatos        | 14      | 14      | ... | 14
EBM                  | Externas  | Talleres de vocería         | 13.2    | 13.2    | ... | 13.2
EBM                  | RRSS      | News Letter                 | 9       | 9       | ... | 9
---------------------|-----------|------------------------------|---------|---------|-----|--------
TOTAL EBM            |           |                              | 1,157.2 | 1,157.2 | ... | 1,157.2
```

---

## 🧮 Metodología de Cálculo de Rentabilidad

### Paso 1: Obtener Ingresos Totales del Mes

**Fuente**: Flujo de Caja 2025, Fila 173

```
Ejemplo Enero 2025:
Total Ingresos = 6,224.25 UF = 209,607,828 pesos
```

### Paso 2: Subdividir Ingresos por Cliente y Área

**Fuente**: Facturación por área 2025 v2.xlsx, hoja `Facturacion_cliente_area`

```
Para cada Cliente-Área:
  Ingresos Cliente-Área = UF/mes del contrato
```

**Ejemplo EBM - Comunicaciones Externas**:
```
Ingresos = 881.2 UF/mes
```

**Validación**:
```
Suma de todos los ingresos Cliente-Área debe = Total Ingresos mes
```

### Paso 3: Calcular Costos Directos (Horas Trabajadas)

**Fuente**: Historial 2024-2025.xlsx, hoja `Horas`

**Para cada Cliente**:
```sql
SELECT
  cliente_id,
  SUM(horas * costo_hora_persona) as costo_directo_uf
FROM registros_horas
WHERE fecha >= '2025-01-01' AND fecha <= '2025-09-30'
GROUP BY cliente_id
```

**Para cada Área**:
```sql
SELECT
  area_id,
  SUM(horas * costo_hora_persona) as costo_directo_uf
FROM registros_horas
WHERE fecha >= '2025-01-01' AND fecha <= '2025-09-30'
GROUP BY area_id
```

**Para cada Cliente-Área**:
```sql
SELECT
  cliente_id,
  area_id,
  SUM(horas * costo_hora_persona) as costo_directo_uf
FROM registros_horas
WHERE fecha >= '2025-01-01' AND fecha <= '2025-09-30'
GROUP BY cliente_id, area_id
```

### Paso 4: Calcular Overhead (Costos Fijos)

**Componentes del Overhead**:

1. **Horas NO asignadas a proyectos** (gap de horas):
   ```
   Para cada persona en cada mes:
     horas_disponibles = 156 (full-time)
     horas_registradas = SUM(horas en registros_horas)
     horas_gap = horas_disponibles - horas_registradas
     costo_gap = horas_gap * costo_hora_persona

   Total overhead por horas no asignadas = SUMA(costo_gap de todas las personas)
   ```

2. **Gastos operacionales mensuales**:

   **FUENTE**: Planilla Flujo de Caja Comsulting 2025.xlsx, hoja "2025", **Fila 119**

   **¿Qué incluye?** (antes de remuneraciones):
   - Arriendo oficinas (UF 239.7 total = 123 + 116.7)
   - Suscripciones (Litoralpress, Talkwalker, G100, etc.)
   - Servicios externalizados (contador, aseo, soporte)
   - Gastos comunes, GTD, aguas, luz
   - Seguros, patentes
   - Banco, comisiones
   - Caja chica
   - Etc.

   **Valores 2025** (Fila 119, columnas 3-11):
   ```
   Enero:      140,860,927 pesos = 3,706.87 UF
   Febrero:    143,080,026 pesos = 3,765.26 UF
   Marzo:      148,295,997 pesos = 3,902.53 UF
   Abril:      149,497,448 pesos = 3,934.14 UF
   Mayo:       142,913,469 pesos = 3,760.88 UF
   Junio:      151,249,384 pesos = 3,980.25 UF
   Julio:      146,459,826 pesos = 3,854.21 UF
   Agosto:     136,211,970 pesos = 3,584.53 UF
   Septiembre: 142,724,307 pesos = 3,755.90 UF

   TOTAL (Ene-Sep): 1,301,293,354 pesos = 34,244.56 UF
   Promedio mensual: 144,588,150 pesos = 3,804.95 UF/mes
   ```

3. **Total Overhead mes**:
   ```
   Overhead Total = Costo horas no asignadas + Gastos operacionales
   ```

### Paso 5: Distribuir Overhead Proporcionalmente a los Ingresos

**IMPORTANTE**: El overhead se distribuye **proporcional a los ingresos**, NO a las horas.

**Fórmula**:
```
Para cada Cliente:
  % participación = Ingresos Cliente / Ingresos Totales
  Overhead Cliente = Overhead Total * % participación
```

**Ejemplo** (asumiendo Overhead Total = 2,000 UF):
```
EBM:
  Ingresos EBM = 1,157.2 UF
  Ingresos Totales = 6,224.25 UF
  % participación = 1,157.2 / 6,224.25 = 18.6%
  Overhead EBM = 2,000 UF * 18.6% = 372 UF
```

**Para Cliente-Área**:
```
EBM - Comunicaciones Externas:
  Ingresos = 881.2 UF
  % participación = 881.2 / 6,224.25 = 14.16%
  Overhead = 2,000 UF * 14.16% = 283.2 UF
```

### Paso 6: Calcular Rentabilidad

**Para cada Cliente**:
```
Costo Total = Costo Directo (HH) + Overhead
Utilidad Neta = Ingresos - Costo Total
Margen % = (Utilidad Neta / Ingresos) * 100
ROI = (Utilidad Neta / Costo Total) * 100
```

**Para cada Área**:
```
Costo Total = Costo Directo (HH) + Overhead
Utilidad Neta = Ingresos - Costo Total
Margen % = (Utilidad Neta / Ingresos) * 100
```

**Para cada Cliente-Área**:
```
Costo Total = Costo Directo (HH) + Overhead
Utilidad Neta = Ingresos - Costo Total
Margen % = (Utilidad Neta / Ingresos) * 100
```

### Paso 7: Verificación de Consistencia

**Condición que DEBE cumplirse**:

```
Suma(Utilidad Neta por Cliente) = Suma(Utilidad Neta por Área) = Utilidad Neta Total

Ejemplo:
- Utilidad Neta Total Empresa = 2,500 UF
- Suma de Utilidad por Clientes = 2,500 UF ✓
- Suma de Utilidad por Áreas = 2,500 UF ✓
```

Si no cuadra, hay un error en:
1. Asignación de ingresos (falta algún cliente/área)
2. Asignación de costos directos
3. Distribución de overhead

---

## 📊 Ejemplo Completo (Enero 2025)

### Datos de entrada:

**Ingresos Totales** (Flujo de Caja):
- Total: 6,224.25 UF

**Gastos Totales** (Flujo de Caja):
- Sueldos: 3,200 UF (ejemplo)
- Gastos operacionales: 500 UF
- Total: 3,700 UF

**Horas trabajadas** (Historial):
- Total horas registradas: 3,500 horas
- Horas disponibles: 37 personas × 156 horas = 5,772 horas
- Horas gap: 5,772 - 3,500 = 2,272 horas
- Costo gap: 2,272 × promedio 20 UF/hora = 454.4 UF (ejemplo)

**Overhead**:
- Gastos operacionales: 500 UF
- Costo horas gap: 454.4 UF
- **Total Overhead: 954.4 UF**

### Cálculo por Cliente (Ejemplo: EBM):

1. **Ingresos** (Facturación por área):
   - Com. Externas: 881.2 UF
   - RRSS: 219 UF (210 + 9)
   - Interna: 14 UF
   - **Total EBM**: 1,114.2 UF

2. **Costo Directo** (Historial 2024-2025):
   - Horas trabajadas para EBM: 500 horas (ejemplo)
   - Costo promedio: 20 UF/hora
   - **Costo Directo EBM**: 500 × 20 = 1,000 UF

3. **Overhead** (proporcional a ingresos):
   - % participación: 1,114.2 / 6,224.25 = 17.9%
   - Overhead: 954.4 × 17.9% = **170.8 UF**

4. **Rentabilidad**:
   - Costo Total: 1,000 + 170.8 = 1,170.8 UF
   - Utilidad Neta: 1,114.2 - 1,170.8 = **-56.6 UF**
   - Margen %: -56.6 / 1,114.2 = **-5.1%** (cliente no rentable)

### Cálculo por Área (Ejemplo: Comunicaciones Externas):

1. **Ingresos** (suma de todos los clientes en Com. Externas):
   - EBM: 881.2 UF
   - Collahuasi: 350 UF
   - AFP Modelo: 225 UF
   - ... (sumar todos)
   - **Total Com. Externas**: 3,438.5 UF (del subtotal en Facturación por área)

2. **Costo Directo** (todas las horas de Com. Externas):
   - Horas: 2,000 horas (ejemplo)
   - **Costo Directo**: 2,000 × 20 = 2,000 UF

3. **Overhead** (proporcional a ingresos):
   - % participación: 3,438.5 / 6,224.25 = 55.3%
   - Overhead: 954.4 × 55.3% = **527.8 UF**

4. **Rentabilidad**:
   - Costo Total: 2,000 + 527.8 = 2,527.8 UF
   - Utilidad Neta: 3,438.5 - 2,527.8 = **910.7 UF**
   - Margen %: 910.7 / 3,438.5 = **26.5%**

### Verificación:

```
Suma(Utilidad por Cliente) debe = Suma(Utilidad por Área) = Utilidad Total Empresa

Utilidad Total = 6,224.25 - 3,700 - 954.4 = 1,569.85 UF

Si:
- Suma utilidad clientes = 1,569.85 UF ✓
- Suma utilidad áreas = 1,569.85 UF ✓

Entonces los cálculos son consistentes.
```

---

## ⚠️ Errores Comunes a Evitar

### 1. Distribuir overhead por horas en lugar de por ingresos

❌ **INCORRECTO**:
```
% participación = Horas Cliente / Horas Totales
Overhead Cliente = Overhead Total * % participación
```

✅ **CORRECTO**:
```
% participación = Ingresos Cliente / Ingresos Totales
Overhead Cliente = Overhead Total * % participación
```

**Razón**: Un cliente puede tener muchas horas pero bajo ingreso (soporte), y otro pocas horas pero alto ingreso (consultoría estratégica). El overhead debe cargarse según el ingreso que genera.

### 2. No incluir horas no asignadas en el overhead

❌ **INCORRECTO**:
```
Overhead = Solo gastos operacionales
```

✅ **CORRECTO**:
```
Overhead = Gastos operacionales + Costo de horas no asignadas
```

**Razón**: Las horas no asignadas son un costo real (se paga a la persona) que no puede cargarse directamente a ningún cliente.

### 3. Calcular costos anuales multiplicando mes actual por meses

❌ **INCORRECTO** (código actual app.py:776):
```python
costo_año_uf = costo_mensual_total_uf * mes_actual  # mes_actual = 10
```

✅ **CORRECTO**:
```python
# Sumar costos reales mes a mes considerando entradas/salidas
costo_año_uf = 0
for mes in range(1, mes_actual + 1):
    personas_activas_mes = get_personas_activas_en_mes(año, mes)
    costo_mes = sum(p.costo_mensual_uf for p in personas_activas_mes)
    costo_año_uf += costo_mes
```

**Razón**: El personal cambia (entradas/salidas), entonces el costo mensual NO es constante.

### 4. No verificar que la suma por cliente = suma por área

❌ **Peligro**: Calcular por cliente y por área de forma independiente sin validar

✅ **CORRECTO**: Siempre verificar:
```python
assert abs(suma_utilidad_clientes - suma_utilidad_areas) < 0.01  # tolerancia de redondeo
```

---

## 🔧 Implementación en AgentTracker

### Tabla `ingresos_mensuales`

```sql
CREATE TABLE ingresos_mensuales (
    id SERIAL PRIMARY KEY,
    servicio_cliente_id INTEGER REFERENCES servicios_cliente(id),
    año INTEGER,
    mes INTEGER,
    ingreso_uf DECIMAL(10,2),
    ingreso_pesos DECIMAL(12,2)
);
```

**Cómo poblar**:
1. Leer `Facturacion_cliente_area` de Excel
2. Para cada Cliente-Área:
   - Crear `ServicioCliente` si no existe
   - Insertar 9 registros (Ene-Sep 2025) en `ingresos_mensuales` con el UF/mes correspondiente

### Función `calcular_overhead_distribuido()`

**Modificación requerida**:

```python
def calcular_overhead_distribuido(año, mes=None):
    """
    Calcula overhead y lo distribuye PROPORCIONALMENTE A LOS INGRESOS
    """
    # 1. Calcular gastos operacionales
    gastos_overhead = GastoOverhead.query.filter_by(año=año)
    if mes:
        gastos_overhead = gastos_overhead.filter_by(mes=mes)
    total_overhead_pesos = sum(g.monto_pesos for g in gastos_overhead.all())
    overhead_operacional_uf = total_overhead_pesos / VALOR_UF_ACTUAL

    # 2. Calcular costo de horas no imputadas (gap)
    costo_horas_no_imputadas_uf = calcular_costo_gap_horas(año, mes)

    # 3. Total overhead
    overhead_total_uf = overhead_operacional_uf + costo_horas_no_imputadas_uf

    # 4. Obtener ingresos totales y por cliente
    ingresos_query = IngresoMensual.query.filter_by(año=año)
    if mes:
        ingresos_query = ingresos_query.filter_by(mes=mes)

    ingresos_por_cliente = {}
    total_ingresos = 0
    for ingreso in ingresos_query.all():
        cliente_id = ingreso.servicio_cliente.cliente_id
        ingresos_por_cliente[cliente_id] = ingresos_por_cliente.get(cliente_id, 0) + ingreso.ingreso_uf
        total_ingresos += ingreso.ingreso_uf

    # 5. Distribuir overhead PROPORCIONALMENTE A INGRESOS
    distribucion_overhead = {}
    for cliente_id, ingresos_cliente in ingresos_por_cliente.items():
        if total_ingresos > 0:
            porcentaje = ingresos_cliente / total_ingresos
            overhead_cliente = overhead_total_uf * porcentaje
        else:
            overhead_cliente = 0
        distribucion_overhead[cliente_id] = round(overhead_cliente, 2)

    return {
        'overhead_total_uf': round(overhead_total_uf, 2),
        'overhead_operacional_uf': round(overhead_operacional_uf, 2),
        'overhead_horas_no_imputadas_uf': round(costo_horas_no_imputadas_uf, 2),
        'total_ingresos': round(total_ingresos, 2),
        'distribucion_por_cliente': distribucion_overhead
    }
```

**Diferencia clave**:
- ❌ Antes: Distribución proporcional a HORAS
- ✅ Ahora: Distribución proporcional a INGRESOS

---

## 📝 Checklist de Validación

Antes de dar por buenos los números, verificar:

- [ ] Ingresos totales de dashboard = Ingresos de Flujo de Caja (Fila 173)
- [ ] Gastos totales de dashboard = Gastos de Flujo de Caja (Fila 119)
- [ ] Suma(Ingresos por Cliente) = Ingresos Totales
- [ ] Suma(Ingresos por Área) = Ingresos Totales
- [ ] Suma(Costos Directos por Cliente) = Total HH registradas × Costo promedio/hora
- [ ] Overhead Total = Gastos operacionales + Costo gap horas
- [ ] Suma(Overhead por Cliente) = Overhead Total
- [ ] Suma(Utilidad por Cliente) = Suma(Utilidad por Área) = Utilidad Total
- [ ] Margen % Total = (Utilidad Total / Ingresos Totales) × 100
- [ ] Ningún cliente tiene overhead > 3× su costo directo (revisar si ocurre)

---

**Última actualización**: 2025-10-30
**Versión**: 1.0
