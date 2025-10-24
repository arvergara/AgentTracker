# Plan de Mejoras - AgentTracker

## 📋 Cambios Solicitados

### 1. Panel de Productividad por Persona
**Objetivo**: Mostrar % de tiempo asignado vs disponible por persona

**Requisitos**:
- Asumir 7 horas diarias como máximo asignable
- Mostrar para cada persona:
  - Total de horas disponibles en el período
  - Horas asignadas a proyectos
  - Porcentaje de ocupación
  - Horas disponibles restantes
- Vista por mes actual y configurable

**Implementación**:
- Nueva ruta: `/productividad/personas`
- Cálculo:
  - Horas disponibles/mes = Días hábiles × 7 horas
  - Horas asignadas = SUM(horas registradas en el mes)
  - % Ocupación = (Horas asignadas / Horas disponibles) × 100
- Template: modificar `productividad.html` o crear nuevo

---

### 2. Rentabilidad para TODOS los Clientes
**Objetivo**: Mostrar rentabilidad de todos los clientes, no solo top 5

**Cambio actual**:
```python
# ANTES: Solo muestra 5 clientes
clientes.slice(0, 10)  # En el gráfico

# DESPUÉS: Mostrar todos
clientes  # Sin límite
```

**Implementación**:
- Modificar template `productividad.html` línea 601 y 391
- Agregar paginación o scroll infinito si son muchos clientes
- Mantener gráfico con top 10 pero tabla con todos

---

### 3. Histórico de Cambios en Servicios + Proyección Ajustada
**Objetivo**: Registrar cambios de valor en servicios y ajustar proyección anual

**Ejemplo**:
- Servicio: Cliente X - Asesoría
- Ene-Sep: 100 UF/mes = 900 UF
- Oct-Dic: 200 UF/mes = 600 UF
- **Proyección 2025**: 900 + 600 = 1,500 UF (no 100×12 = 1,200 UF)

**Implementación**:

#### A. Nueva tabla en BD: `historico_servicios`
```sql
CREATE TABLE historico_servicios (
    id SERIAL PRIMARY KEY,
    servicio_cliente_id INTEGER REFERENCES servicios_cliente(id),
    valor_anterior_uf FLOAT,
    valor_nuevo_uf FLOAT,
    fecha_cambio DATE NOT NULL,
    usuario_id INTEGER REFERENCES personas(id),
    motivo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### B. Modificar endpoint de edición de servicios
- Antes de actualizar `servicios_cliente.valor_mensual_uf`
- Insertar registro en `historico_servicios`
- Guardar: valor anterior, valor nuevo, fecha, usuario

#### C. Nueva lógica de proyección anual
```python
def proyeccion_anual_servicio(servicio_id, año):
    # Obtener histórico de cambios
    cambios = HistoricoServicio.query.filter_by(
        servicio_cliente_id=servicio_id
    ).filter(
        extract('year', HistoricoServicio.fecha_cambio) == año
    ).order_by(HistoricoServicio.fecha_cambio).all()

    proyeccion = 0
    mes_inicio = 1
    valor_actual = servicio.valor_mensual_uf

    for cambio in cambios:
        mes_cambio = cambio.fecha_cambio.month
        # Proyectar con valor anterior hasta mes del cambio
        meses_con_valor_anterior = mes_cambio - mes_inicio
        proyeccion += cambio.valor_anterior_uf * meses_con_valor_anterior

        mes_inicio = mes_cambio
        valor_actual = cambio.valor_nuevo_uf

    # Proyectar resto del año con valor actual
    meses_restantes = 13 - mes_inicio
    proyeccion += valor_actual * meses_restantes

    return proyeccion
```

#### D. Modificar dashboard/rentabilidad
- Usar `proyeccion_anual_servicio()` en lugar de `valor_mensual_uf × 12`
- Mostrar en tooltip/detalle: "Proyección ajustada por cambios"

---

## 🔧 Orden de Implementación

### Fase 1: Productividad por Persona (más rápido)
1. Crear ruta `/productividad/personas`
2. Calcular horas disponibles/asignadas
3. Renderizar en template existente o nuevo

**Tiempo estimado**: 30 min

### Fase 2: Rentabilidad Todos los Clientes (muy rápido)
1. Modificar template para quitar límite
2. Agregar paginación si necesario

**Tiempo estimado**: 15 min

### Fase 3: Histórico de Servicios (más complejo)
1. Crear migración para tabla `historico_servicios`
2. Modificar modelo de datos (app.py)
3. Modificar endpoint de edición de servicios
4. Crear función de proyección ajustada
5. Modificar dashboards/rentabilidad para usar proyección

**Tiempo estimado**: 1-2 horas

---

## ¿Proceder con la implementación?

¿Quieres que empiece con Fase 1 (Productividad por Persona)?
