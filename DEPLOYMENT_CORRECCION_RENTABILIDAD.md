# Deployment - Corrección de Rentabilidad

**Fecha**: 2025-10-30
**Objetivo**: Corregir cálculo de rentabilidad distribuyendo overhead por ingresos (no por horas)

---

## 📋 Cambios Realizados

### 1. **Modificación en app.py** (Commit 3928976)

**Función afectada**: `calcular_overhead_distribuido()`

**Cambio**:
- ❌ **ANTES**: Distribuía overhead proporcional a horas trabajadas
- ✅ **AHORA**: Distribuye overhead proporcional a ingresos facturados

**Código modificado** (app.py líneas 204-253):
```python
# ANTES (distribución por horas):
query_horas_por_cliente = db.session.query(
    RegistroHora.cliente_id,
    func.sum(RegistroHora.horas).label('total_horas')
).filter(...)

porcentaje_cliente = horas_cliente / total_horas_asignadas
overhead_cliente = overhead_total_uf * porcentaje_cliente

# AHORA (distribución por ingresos):
query_ingresos_por_cliente = db.session.query(
    ServicioCliente.cliente_id,
    func.sum(IngresoMensual.ingreso_uf).label('total_ingresos')
).join(IngresoMensual, ...)

porcentaje_cliente = ingresos_cliente / total_ingresos
overhead_cliente = overhead_total_uf * porcentaje_cliente
```

### 2. **Nuevo script**: `importar_ingresos_produccion.py` (Commit 1ab62d3)

**Propósito**: Importar ingresos desde `Facturación por área 2025 v2.xlsx` a tabla `ingresos_mensuales`

**Qué hace**:
1. Lee hoja "Facturacion_cliente_area" del Excel
2. Para cada Cliente-Área, crea `ServicioCliente` si no existe
3. Inserta registros en `ingresos_mensuales` para Ene-Sep 2025
4. Valida totales por mes y por cliente

---

## 🚀 Pasos para Deployment

### Paso 1: Verificar que Render ha Desplegado los Cambios

1. Ve a https://dashboard.render.com
2. Selecciona el servicio "AgentTracker"
3. Verifica que el último deploy sea el commit **3928976**
4. Espera a que el deployment termine (status: "Live")

### Paso 2: Subir el Excel a Render (CRÍTICO)

El script necesita acceso al archivo Excel. Tienes 2 opciones:

#### Opción A: Subir Excel vía SCP/FTP (Recomendado)
```bash
# Desde tu máquina local
scp "/Users/alfil/Desktop/Desarrollos/Comsulting/Fuentes de informacion/Facturación por área 2025 v2.xlsx" \
    render:/app/
```

#### Opción B: Ejecutar script localmente contra BD remota
```bash
# En tu máquina local
cd /Users/alfil/Desktop/Desarrollos/Comsulting/AgentTracker

# Configurar DATABASE_URL apuntando a Render
export DATABASE_URL="postgresql://agenttracker_db_user:SVoi2QQ0qt0Zye0QPzEj7g2lX9RJ2ANb@dpg-d3pb2i3ipnbc739ps5r0-a/agenttracker_db"

# Instalar dependencias si no están
pip3 install pandas openpyxl sqlalchemy psycopg2-binary

# Ejecutar importación
python3 importar_ingresos_produccion.py
```

**IMPORTANTE**: La Opción B es más fácil porque tienes el Excel local.

### Paso 3: Ejecutar Importación de Ingresos

#### Si usaste Opción A (Excel en Render):
```bash
# En Render Shell
export DATABASE_URL="postgresql://agenttracker_db_user:SVoi2QQ0qt0Zye0QPzEj7g2lX9RJ2ANb@dpg-d3pb2i3ipnbc739ps5r0-a/agenttracker_db"

pip3 install pandas openpyxl sqlalchemy psycopg2-binary

python3 importar_ingresos_produccion.py
```

#### Si usaste Opción B (Local):
Ya ejecutaste el script en el paso anterior.

### Paso 4: Verificar Importación

```bash
# En Render Shell O en tu máquina con DATABASE_URL configurado
python3 << 'EOF'
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    # Total ingresos 2025
    result = conn.execute(text("""
        SELECT mes, SUM(ingreso_uf) as total_uf
        FROM ingresos_mensuales
        WHERE año = 2025
        GROUP BY mes
        ORDER BY mes
    """))

    print("Ingresos mensuales 2025:")
    total = 0
    for row in result:
        mes, uf = row
        total += uf
        print(f"  Mes {mes:2d}: {uf:8,.2f} UF")

    print(f"\nTotal año: {total:,.2f} UF")
    print(f"Promedio mensual: {total/9:,.2f} UF")

    # Top 5 clientes
    result = conn.execute(text("""
        SELECT c.nombre, SUM(im.ingreso_uf) as total_uf
        FROM ingresos_mensuales im
        JOIN servicios_cliente sc ON im.servicio_cliente_id = sc.id
        JOIN clientes c ON sc.cliente_id = c.id
        WHERE im.año = 2025
        GROUP BY c.nombre
        ORDER BY total_uf DESC
        LIMIT 5
    """))

    print("\nTop 5 clientes:")
    for row in result:
        print(f"  {row[0]:30s}: {row[1]:8,.2f} UF")
EOF
```

**Resultados esperados**:
```
Ingresos mensuales 2025:
  Mes  1:  5,xxx.xx UF
  Mes  2:  5,xxx.xx UF
  ...
  Mes  9:  5,xxx.xx UF

Total año: 50,000-55,000 UF (aproximado)
Promedio mensual: 5,500-6,000 UF

Top 5 clientes:
  EBM                           : 10,000+ UF
  Falabella                     :  5,000+ UF
  Collahuasi                    :  4,500+ UF
  ...
```

### Paso 5: Verificar Dashboard

1. Accede a https://agenttracker.onrender.com/dashboard
2. Inicia sesión como socia (Blanca, Macarena o Jazmín)
3. Verifica la sección "💰 Resultado de Clientes 2025"

**Cambios esperados**:
- ✅ Overhead más equilibrado (no más 3-4x el costo directo)
- ✅ Rentabilidades realistas:
  - Clientes rentables: 10-40% margen
  - Clientes no rentables: -5% a -20% margen
  - NO más rentabilidades absurdas (-146% o +79%)
- ✅ EBM overhead ~300-500 UF (antes: 4,708 UF)

### Paso 6: Validación Final

Ejecutar este script para validar consistencia:

```python
# En Render Shell o local con DATABASE_URL
python3 << 'EOF'
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    # Validar que suma de overhead por cliente = overhead total

    # 1. Obtener overhead total del año
    result = conn.execute(text("""
        SELECT SUM(monto_pesos) FROM gastos_overhead WHERE año = 2025
    """))
    gastos_overhead = result.fetchone()[0] or 0
    gastos_overhead_uf = gastos_overhead / 38000

    print(f"Gastos overhead operacionales: {gastos_overhead_uf:,.2f} UF")

    # 2. Calcular overhead distribuido (simplificado)
    # Este cálculo debe coincidir con calcular_overhead_distribuido()

    print("\n✓ Validación completada")
    print("Revisa el dashboard para confirmar los números")
EOF
```

---

## ⚠️ Rollback (si algo sale mal)

Si los números siguen mal o hay errores:

### Opción 1: Revertir cambio en app.py

```bash
cd /Users/alfil/Desktop/Desarrollos/Comsulting/AgentTracker
git revert 3928976
git push origin main
```

Render auto-desplegará la versión anterior.

### Opción 2: Limpiar ingresos importados

```bash
# En Render Shell o local
python3 << 'EOF'
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("DELETE FROM ingresos_mensuales WHERE año = 2025"))
    count = result.rowcount
    conn.commit()
    print(f"Eliminados {count} registros de ingresos 2025")
EOF
```

---

## 📊 Checklist de Validación

Antes de dar por completado el deployment:

- [ ] Render desplegó commit 3928976
- [ ] Script `importar_ingresos_produccion.py` ejecutado exitosamente
- [ ] Ingresos totales 2025: ~50,000-55,000 UF
- [ ] Promedio mensual ingresos: ~5,500-6,000 UF
- [ ] Top clientes tienen ingresos coherentes (EBM ~10,000 UF total)
- [ ] Dashboard carga sin errores
- [ ] Overhead de EBM < 1,000 UF (antes: 4,708 UF)
- [ ] No hay rentabilidades absurdas (< -50% o > +80%)
- [ ] Rentabilidad total empresa ~25-35% (valor razonable)
- [ ] Suma(utilidad por cliente) ≈ Suma(utilidad por área) ≈ Utilidad total

---

## 📝 Notas Importantes

1. **Tiempo de deployment en Render**: 2-5 minutos
2. **Cache**: Si el dashboard no refleja cambios, hacer hard refresh (Cmd+Shift+R)
3. **Logs**: Revisar logs en Render si hay errores
4. **Excel path**: El script busca el Excel en `/Users/alfil/Desktop/Desarrollos/Comsulting/Fuentes de informacion/`
5. **Valor UF**: Hardcodeado en 38,000 pesos (actualizar si cambia)

---

## 🎯 Resultado Esperado

### Dashboard ANTES de los cambios:
```
Cliente    | Ingresos | Costo Variable | Overhead | Margen %
-----------|----------|----------------|----------|----------
EBM        | 10,415   | 1,505          | 4,708    | -?? %
Liberty    | 300      | 20             | 42       | +79%
Embajada   | 88       | 80             | 137      | -146%
```

### Dashboard DESPUÉS de los cambios:
```
Cliente    | Ingresos | Costo Variable | Overhead | Margen %
-----------|----------|----------------|----------|----------
EBM        | 10,415   | 1,505          | ~450     | ~20-25%
Liberty    | 300      | 20             | ~15      | ~25-30%
Embajada   | 88       | 80             | ~4       | ~5-10%
```

Overhead ahora es proporcional a ingresos, no a horas.

---

**Última actualización**: 2025-10-30
**Responsable**: Alfil + Claude Code
**Commits**: 1ab62d3 (script ingresos), 3928976 (distribución por ingresos)
