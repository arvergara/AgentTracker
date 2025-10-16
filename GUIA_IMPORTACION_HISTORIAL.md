# Guía de Importación de Historial 2024-2025

## Resumen

Este documento explica cómo importar el historial de horas de Harvest (2024-2025) a AgentTracker.

## Archivos Involucrados

- **CSV fuente**: `/Users/alfil/Library/CloudStorage/GoogleDrive-andres.vergara@maindset.cl/Mi unidad/Comsulting/Historial2024-2025.csv`
- **Script de importación**: `importar_historial_2024_2025.py`
- **Script de áreas**: `crear_areas_iniciales.py`

## Estructura del CSV

El CSV exportado de Harvest contiene:
- **Total registros**: 105,504 registros de horas
- **Período**: Enero 2024 - Septiembre 2025
- **Formato**: Comas como separador decimal (formato chileno)

### Columnas Importantes

- `Date`: Fecha del registro
- `Client`: Nombre del cliente
- `Project`: Nombre del proyecto/servicio
- `Task`: Tarea realizada
- `Hours`: Horas trabajadas (con coma como decimal)
- `First Name` / `Last Name`: Nombre de la persona

## Cambio Importante: Octubre 2024

**ANTES de Octubre 2024**:
- `Client` y `Project` tienen el mismo nombre
- Ejemplo: Client="GUACOLDA", Project="GUACOLDA"
- El sistema asigna área="Comunicaciones" por defecto

**DESDE Octubre 2024**:
- `Client` es el nombre del cliente
- `Project` indica el servicio/área específica
- Ejemplo: Client="FALABELLA", Project="RRSS"
- El sistema determina el área según el nombre del proyecto

## Proceso de Importación

### Paso 1: Preparación

El sistema ya tiene:
- ✅ 38 usuarios creados e inicializados
- ✅ Jerarquía organizacional configurada
- ✅ 5 áreas estándar de Comsulting
- ✅ 11 servicios estándar

### Paso 2: Ejecutar Importación

```bash
cd AgentTracker
python importar_historial_2024_2025.py
```

**Tiempo estimado**: 10-15 minutos (105K registros)

### Paso 3: Lo que hace el script

1. **Lee el CSV línea por línea**
   - Procesa cada registro de horas
   - Muestra progreso cada 1000 registros

2. **Busca y asocia personas**
   - Match por nombre y apellido
   - Registros sin match se saltan

3. **Crea clientes automáticamente**
   - Si el cliente no existe, lo crea
   - Determina tipo (permanente/spot)

4. **Maneja áreas y servicios**
   - Antes de Oct 2024: área por defecto
   - Desde Oct 2024: determina área según project

5. **Crea registros de horas**
   - Asocia persona + cliente + área + servicio + tarea
   - Guarda fecha y horas trabajadas

### Paso 4: Verificación

El script muestra al final:
- Total registros procesados
- Total registros importados
- Total registros saltados
- Clientes creados
- Personas no encontradas
- Rango de fechas

## Mapeo de Áreas por Proyecto

El script determina automáticamente el área según palabras clave en el nombre del proyecto:

| Palabras Clave | Área Asignada |
|----------------|---------------|
| "rrss", "social" | Redes Sociales |
| "diseño", "design" | Diseño |
| "asuntos", "públicos" | Asuntos Públicos |
| "interna", "interno" | Internas |
| (otros) | Externas |

## Manejo de Errores

### Personas No Encontradas

Si una persona del CSV no existe en la BD:
- El registro se salta
- Se agrega a la lista de "Personas no encontradas"
- Al final se muestra el resumen

**Solución**: Verificar nombres en el CSV vs nombres en la BD

### Horas con Valor 0

Los registros con 0 horas se saltan automáticamente.

### Datos Faltantes

- Si falta `Date`: registro saltado
- Si falta `Client`: registro saltado
- Si falta `Project`: se usa el Client como proyecto
- Si falta `Task`: se asigna "Tarea general"

## Resultados Esperados

Después de la importación exitosa:

```
📊 Registros:
  Procesados: 105,504
  Importados: ~100,000-105,000
  Saltados: 0-5,000

🏢 Clientes: 50-100 clientes únicos
⚙️  Servicios: 100-200 servicios
📋 Tareas: 200-500 tareas únicas

📅 Rango de fechas:
  Desde: 2024-01-01
  Hasta: 2025-09-30
```

## Consultas Útiles Post-Importación

### Ver clientes más activos

```python
from app import app, db, Cliente, RegistroHora
from sqlalchemy import func

with app.app_context():
    top_clientes = db.session.query(
        Cliente.nombre,
        func.sum(RegistroHora.horas).label('total_horas')
    ).join(RegistroHora).group_by(Cliente.id).order_by(
        func.sum(RegistroHora.horas).desc()
    ).limit(10).all()

    for cliente, horas in top_clientes:
        print(f"{cliente}: {horas:.1f} horas")
```

### Ver horas por persona

```python
from app import app, db, Persona, RegistroHora
from sqlalchemy import func

with app.app_context():
    horas_por_persona = db.session.query(
        Persona.nombre,
        func.sum(RegistroHora.horas).label('total_horas')
    ).join(RegistroHora).group_by(Persona.id).order_by(
        func.sum(RegistroHora.horas).desc()
    ).all()

    for persona, horas in horas_por_persona:
        print(f"{persona}: {horas:.1f} horas")
```

### Ver distribución por área

```python
from app import app, db, Area, RegistroHora
from sqlalchemy import func

with app.app_context():
    por_area = db.session.query(
        Area.nombre,
        func.sum(RegistroHora.horas).label('total_horas')
    ).join(RegistroHora).group_by(Area.id).all()

    for area, horas in por_area:
        print(f"{area}: {horas:.1f} horas")
```

## Troubleshooting

### Error: "No module named 'app'"

```bash
cd AgentTracker
python importar_historial_2024_2025.py
```

### Error: "No such file"

Verifica la ruta del CSV en el script:
```python
CSV_PATH = '../Historial2024-2025.csv'
```

### Importación muy lenta

Es normal con 105K registros. El script hace commit cada 1000 registros para optimizar.

### Memoria insuficiente

El script procesa línea por línea, no debería haber problemas de memoria.

## Siguientes Pasos

Después de importar el historial:

1. **Crear Servicios-Cliente**
   - Asociar clientes con sus servicios contratados
   - Definir valores mensuales en UF

2. **Cargar Ingresos Mensuales**
   - Importar facturación por mes

3. **Calcular Rentabilidad**
   - Con horas + costos + facturación = rentabilidad

4. **Generar Reportes**
   - Productividad por persona
   - Rentabilidad por cliente
   - Capacidad del equipo

## Notas Importantes

1. **Backup**: Siempre hacer backup antes de importaciones masivas
2. **Tiempo**: La importación puede tomar 10-15 minutos
3. **Validación**: Verificar algunos registros manualmente después
4. **Duplicados**: El script no verifica duplicados, ejecutar solo una vez

---

**Creado**: 15 de octubre de 2025
**Versión**: 1.0
