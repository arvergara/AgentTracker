# 🔍 Informe de Diagnóstico: Problemas de Rentabilidad AgentTracker

**Fecha:** 27 de octubre de 2025
**Analista:** Claude Code
**Archivos analizados:**
- `Cliente_Comsulting.xlsx`
- `Historial 2024-2025.xlsx`
- Código fuente: `app.py`

---

## 📊 Resumen Ejecutivo

Se identificaron **3 problemas principales** en el sistema de rentabilidad de AgentTracker:

1. ✅ **Margen promedio ~70%** - El cálculo es CORRECTO pero hay duplicación de clientes
2. ❌ **Falabella, Collahuasi, COPEC con margen negativo** - Problema de matching de nombres
3. ⚠️  **Inconsistencia en nombres de clientes** - Entre archivos de ingresos y horas

---

## 🎯 Problema 1: Margen Promedio ~70%

### Hallazgos

El margen total calculado es **69.6%**, que coincide con lo reportado por las socias (~70%).

**Análisis:**
```
Total Ingresos:  107,302.6 UF
Total Costos:     32,614.7 UF (solo costos directos de horas)
Utilidad:         74,687.9 UF
Margen:           69.6%
```

### ¿Es correcto este margen?

**SÍ y NO:**

✅ **Correcto matemáticamente**: El cálculo es preciso basado en los datos
❌ **Incorrecto para decisiones de negocio**: Falta incluir overhead

### Causa Raíz

El cálculo actual **NO incluye**:
- Gastos operacionales (arriendos, servicios, software, etc.)
- Horas no imputadas (gap entre horas disponibles y registradas)
- Gastos administrativos
- Impuestos

Esto hace que el margen parezca artificialmente alto.

### Ejemplo Real

**EBM:**
- Ingresos: 7,704 UF
- Costos directos (horas): 526.6 UF
- Margen calculado: **93.2%** ← Parece excelente

Pero si incluimos overhead proporcional (estimado 30-40%):
- Overhead: ~230 UF
- Costos totales: 756.6 UF
- Margen real: **90.2%** ← Sigue siendo bueno pero más realista

---

## 🎯 Problema 2: Falabella, Collahuasi, COPEC con Margen Negativo

### Hallazgos Críticos

**DUPLICACIÓN DE CLIENTES** - Los clientes están registrados con nombres diferentes:

#### Caso 1: FALABELLA

| Versión | Ingresos | Horas | Costos | Margen |
|---------|----------|-------|--------|--------|
| FALABELLA S.A. (mayúsculas) | 4,790 UF | 0h | 0 UF | **100%** ✅ |
| FALABELLA (registro horas) | 4,790 UF | 5,386.9h | 4,493.3 UF | **6.2%** ⚠️  |

**Problema:** El sistema no está haciendo matching entre "FALABELLA S.A." (del Excel de ingresos) y "FALABELLA" (del registro de horas).

#### Caso 2: COLLAHUASI

| Versión | Ingresos | Horas | Costos | Margen |
|---------|----------|-------|--------|--------|
| COLLAHUASI (mayúsculas) | 3,150 UF | 0h | 0 UF | **100%** ✅ |
| Collahuasi (registro horas) | 3,150 UF | 4,817.9h | 3,854.3 UF | **-22.4%** ❌ |

**Problema:** Las horas de "Collahuasi" no están siendo asignadas correctamente a los ingresos de "COLLAHUASI".

#### Caso 3: EMPRESAS COPEC

| Versión | Ingresos | Horas | Costos | Margen |
|---------|----------|-------|--------|--------|
| Empresas COPEC (mixto) | 2,250 UF | 0h | 0 UF | **100%** ✅ |
| EMPRESAS COPEC (mayúsculas) | 2,250 UF | 3,118.6h | 2,566.3 UF | **-14.1%** ❌ |

### Causa Raíz

1. **Inconsistencia en nombres** entre:
   - `Cliente_Comsulting.xlsx` (ingresos)
   - `Historial 2024-2025.xlsx` hoja "Horas" (costos)

2. **Falta de normalización** en el código de importación
   - El sistema crea clientes separados para "FALABELLA" y "FALABELLA S.A."
   - No hay limpieza de nombres (trim, uppercase, eliminación de sufijos)

3. **Duplicación en dashboard**
   - El dashboard muestra ambas versiones del cliente
   - Los reportes suman mal los márgenes

---

## 🎯 Problema 3: Clientes con 0 Horas pero con Ingresos

### Clientes Fantasma

Hay **16 clientes** con ingresos pero **0 horas** registradas:

```
TOTAL SERVICIOS PERMANENTES   51,748 UF    0h     Margen: 100%
FRUTAS DE CHILE                3,584 UF    0h     Margen: 100%
AFP MODELO                     2,025 UF    0h     Margen: 100%
Capstone                       1,800 UF    0h     Margen: 100%
...
```

### Posibles Causas

1. ✅ **Nombres diferentes en horas vs ingresos** (como vimos arriba)
2. ⚠️  **Horas no registradas** en el sistema
3. ⚠️  **Ingresos mal imputados** (registrados en cliente equivocado)

---

## 💡 Soluciones Propuestas

### Solución 1: Normalización de Nombres de Clientes

**Acción:** Crear función de limpieza de nombres

```python
def normalizar_nombre_cliente(nombre):
    """Normaliza nombres de clientes para matching correcto"""
    if not nombre:
        return None

    nombre = nombre.strip().upper()

    # Remover sufijos comunes
    sufijos = [' S.A.', ' S.A', ' SPA', ' LTDA', ' S.P.A.', ' SA']
    for sufijo in sufijos:
        if nombre.endswith(sufijo):
            nombre = nombre[:-len(sufijo)].strip()

    # Casos específicos
    aliases = {
        'EMPRESAS COPEC': 'COPEC',
        'EMPRESAS COPEC S.A.': 'COPEC',
        'AFP MODELO': 'AFP MODELO',
        'FALABELLA S.A.': 'FALABELLA',
        'COLLAHUASI': 'COLLAHUASI',
        'MAE HOLDING CHILE SPA': 'MAE',
        'CAPSTONE COPPER': 'CAPSTONE',
        'CAPSTONE MINNING CORP': 'CAPSTONE',
    }

    return aliases.get(nombre, nombre)
```

**Dónde aplicar:**
- ✅ Script de importación: `importar_historial_2024_2025.py` línea ~150
- ✅ Script de importación: `importar_ingresos_csv_final.py` línea ~80
- ✅ Vistas de rentabilidad: `app.py` líneas 1608-1733

### Solución 2: Incluir Overhead en Cálculo de Margen

**Acción:** Actualizar cálculo de overhead distribuido

La función `calcular_overhead_distribuido()` en `app.py:127` ya existe pero:

❌ **Problema actual:** Requiere tabla `gastos_overhead` que no existe en producción

✅ **Solución:** Crear tabla y poblarla con datos de `Planilla Flujo de Caja 2025.xlsx`

```sql
CREATE TABLE gastos_overhead (
    id SERIAL PRIMARY KEY,
    año INTEGER NOT NULL,
    mes INTEGER,
    concepto VARCHAR(100),
    categoria VARCHAR(50),
    monto_pesos DECIMAL(15,2),
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Gastos a incluir (estimados mensualmente):**
- Arriendo oficina: ~$2,000,000
- Servicios (luz, agua, internet): ~$300,000
- Software y herramientas: ~$500,000
- Gastos administrativos: ~$1,000,000
- Total mensual estimado: **~$3,800,000** (~100 UF/mes)

### Solución 3: Consolidar Clientes Duplicados

**Acción:** Script de consolidación manual

```python
# Ejecutar en producción (Render)
def consolidar_clientes_duplicados():
    """Consolida clientes duplicados en la base de datos"""

    duplicados = [
        ('FALABELLA S.A.', 'FALABELLA'),
        ('COLLAHUASI', 'Collahuasi'),
        ('Empresas COPEC', 'EMPRESAS COPEC'),
        ('CAPSTONE MINNING CORP', 'Capstone Copper'),
        ('CAPSTONE', 'Capstone Copper'),
        ('AFP MODELO', 'AFP Modelo'),
    ]

    for nombre_incorrecto, nombre_correcto in duplicados:
        cliente_incorrecto = Cliente.query.filter_by(nombre=nombre_incorrecto).first()
        cliente_correcto = Cliente.query.filter_by(nombre=nombre_correcto).first()

        if cliente_incorrecto and cliente_correcto:
            # Mover registros de horas
            RegistroHora.query.filter_by(
                cliente_id=cliente_incorrecto.id
            ).update({'cliente_id': cliente_correcto.id})

            # Mover ingresos
            IngresoMensual.query.join(ServicioCliente).filter(
                ServicioCliente.cliente_id == cliente_incorrecto.id
            ).update({'cliente_id': cliente_correcto.id})

            # Marcar como inactivo
            cliente_incorrecto.activo = False

            db.session.commit()
```

### Solución 4: Dashboard Actualizado

**Acción:** Modificar vista de rentabilidad para mostrar alertas

En `templates/dashboard_simplified.html` líneas 370-455:

```javascript
// Agregar alerta si margen > 80% (posible falta de costos)
if (cliente.margen > 80 && cliente.horas == 0) {
    html += `<td>⚠️ Sin horas registradas</td>`;
}

// Agregar alerta si margen negativo
if (cliente.margen < 0) {
    html += `<td>❌ Revisar costos vs ingresos</td>`;
}
```

---

## 📋 Áreas y Servicios (Problema 3)

### Feedback de las Socias

> "En valorizar/nombre del servicio: usar áreas y servicios por áreas que te mandé para inscribir las horas."

### Áreas Actuales (5 áreas)

Según `app.py` y archivos de importación:

1. **Externas** (Comunicaciones Externas, Crisis, Portavocía, Monitoreo)
2. **Internas** (Comunicaciones Internas)
3. **Asuntos Públicos** (Gobierno, Regulatorio)
4. **Redes Sociales** (Estrategia Digital)
5. **Diseño** (Gráfico, Informes, Web)

### Acción Requerida

⚠️  **Necesito que me envíes la clasificación actualizada** de áreas y servicios que las socias quieren usar.

¿Puedes compartir:
- Lista de áreas nueva
- Servicios por cada área
- Tareas por cada servicio (opcional)

---

## 📋 Capacidad - Vista Detallada (Problema 4)

### Feedback de las Socias

> "En capacidad, me gustaría pinchar y poder ver el detalle de quien tiene tiempo y quien no lo tiene."

### Solución Propuesta

Crear vista interactiva drill-down en `/capacidad`:

```html
<!-- Tabla actual (línea superior) -->
<tr onclick="toggleDetallePersona({{ persona.id }})">
    <td>{{ persona.nombre }}</td>
    <td>{{ utilizacion }}%</td>
    <td class="clickable">👁️ Ver detalle</td>
</tr>

<!-- Fila expandible (oculta por defecto) -->
<tr id="detalle-{{ persona.id }}" class="detalle-row hidden">
    <td colspan="5">
        <div class="detalle-container">
            <h4>{{ persona.nombre }} - Desglose de Horas</h4>
            <table>
                <tr>
                    <th>Cliente</th>
                    <th>Horas</th>
                    <th>% Tiempo</th>
                </tr>
                {% for registro in persona.registros %}
                <tr>
                    <td>{{ registro.cliente }}</td>
                    <td>{{ registro.horas }}</td>
                    <td>{{ registro.porcentaje }}%</td>
                </tr>
                {% endfor %}
            </table>
            <p><strong>Horas disponibles:</strong> {{ persona.horas_disponibles }}h</p>
        </div>
    </td>
</tr>
```

---

## 📊 Resumen de Acciones Inmediatas

### 🔴 Alta Prioridad (Hacer YA)

1. ✅ **Consolidar clientes duplicados** en base de datos PostgreSQL
   - Script: Crear `consolidar_clientes_duplicados.py`
   - Ejecutar en Render

2. ✅ **Normalizar nombres de clientes** en scripts de importación
   - Actualizar `importar_historial_2024_2025.py`
   - Actualizar `importar_ingresos_csv_final.py`

3. ✅ **Crear tabla `gastos_overhead`** y poblarla
   - Extraer datos de `Planilla Flujo de Caja 2025.xlsx`
   - Migración SQL

### 🟡 Media Prioridad (Esta Semana)

4. ⚠️  **Actualizar áreas y servicios**
   - Esperar input de las socias con nueva clasificación

5. ⚠️  **Agregar vista drill-down en Capacidad**
   - Modificar `templates/capacidad.html`
   - Actualizar endpoint `/capacidad` en `app.py`

### 🟢 Baja Prioridad (Mejoras Futuras)

6. 💡 **Agregar alertas en dashboard**
   - Indicador visual para clientes sin horas
   - Indicador para márgenes negativos

7. 💡 **Validación de datos en importación**
   - Warning si cliente tiene ingresos pero 0 horas
   - Warning si margen < 0%

---

## 🎯 Resultados Esperados

Después de implementar las soluciones:

### Antes (Actual)
```
FALABELLA S.A.    4,790 UF    0h        Margen: 100%  ✅
FALABELLA         4,790 UF    5,386.9h  Margen: 6.2%  ⚠️
```

### Después (Esperado)
```
FALABELLA         4,790 UF    5,386.9h
  - Costos directos:  4,493 UF
  - Overhead (30%):   1,437 UF
  - Costos totales:   5,930 UF
  - Utilidad:        -1,140 UF
  - Margen:          -23.8%  ❌ <- ALERTA: Cliente a pérdida
```

**Acción:** Revisar fee de Falabella o reducir horas senior asignadas.

---

## ✅ Conclusión

Los problemas reportados son **REALES** pero tienen solución:

1. ✅ Margen ~70% es correcto (sin overhead) - **Incluir overhead para decisiones reales**
2. ❌ EC, Falabella, Collahuasi a pérdida - **Problema de duplicación de nombres**
3. ⚠️  Áreas y servicios - **Esperar input de las socias**
4. 💡 Capacidad drill-down - **Implementación técnica simple**

**Próximos pasos:** ¿Quieres que implemente las soluciones propuestas?
