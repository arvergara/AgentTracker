# Guía de Uso - Sistema de Proyectos

## 📋 Tabla de Contenidos
1. [Introducción](#introducción)
2. [Migración de Datos](#migración-de-datos)
3. [Gestión de Proyectos](#gestión-de-proyectos)
4. [Asignación de Personas](#asignación-de-personas)
5. [Registro de Horas](#registro-de-horas)
6. [Análisis de Rentabilidad](#análisis-de-rentabilidad)
7. [API Endpoints](#api-endpoints)

---

## Introducción

El sistema de proyectos permite gestionar múltiples proyectos por cliente, asignar personas a proyectos específicos y calcular rentabilidad y productividad a nivel de proyecto.

### Características Principales

- **Proyectos Multi-Cliente**: Un cliente puede tener múltiples proyectos
- **Asignación Flexible**: Una persona puede trabajar en varios proyectos simultáneamente
- **Rentabilidad por Proyecto**: Cálculo preciso de margen, ROI y utilidad por proyecto
- **Productividad Individual**: Métricas de productividad por persona en cada proyecto
- **Presupuesto y Control**: Seguimiento de presupuesto vs real

---

## Migración de Datos

### Paso 1: Backup de la Base de Datos

Antes de migrar, haz un backup de tu base de datos actual:

```bash
cp comsulting.db comsulting_backup_$(date +%Y%m%d).db
```

### Paso 2: Ejecutar la Migración

El script de migración creará automáticamente proyectos "General" para cada cliente existente:

```bash
cd /path/to/AgentTracker
python migrate_to_proyectos.py
```

El script te pedirá confirmación antes de proceder.

### Paso 3: Validación

El script automáticamente validará que:
- Todos los registros de horas tengan proyecto asignado
- Las facturas estén asociadas a proyectos
- Las asignaciones de personas se hayan creado correctamente

### ¿Qué hace la migración?

Para cada cliente existente:
1. Crea un proyecto con código `CLI-GEN-2025-XX`
2. Migra todos los registros de horas al proyecto
3. Migra todas las facturas al proyecto
4. Crea asignaciones automáticas para cada persona que trabajó en el cliente

**Ejemplo:**
```
Cliente: "Banco Nacional"
  → Proyecto creado: "Proyecto General Banco Nacional" (BAN-GEN-2025-01)
  → 450 horas migradas
  → 3 facturas migradas
  → 5 personas asignadas automáticamente
```

---

## Gestión de Proyectos

### Crear un Nuevo Proyecto

1. Ve a **Proyectos** → **+ Nuevo Proyecto**
2. Completa el formulario:
   - **Cliente** (requerido)
   - **Nombre del Proyecto** (requerido)
   - **Código** (opcional, se genera automáticamente)
   - **Servicio** (opcional)
   - **Tipo**: Permanente, Spot o Interno
   - **Fechas**: Inicio y fin estimado
   - **Presupuesto en UF**
   - **Margen Objetivo** (por defecto 12.5%)

3. Click en **Crear Proyecto**

### Códigos de Proyecto

El sistema genera automáticamente códigos con el formato:
```
[3 letras del cliente]-PRY-[año]-[número]

Ejemplos:
- BAN-PRY-2025-01 (Banco Nacional, proyecto 1)
- MET-PRY-2025-02 (Metrogas, proyecto 2)
```

### Estados de Proyecto

- **Activo**: Proyecto en ejecución
- **Pausado**: Temporalmente detenido
- **Cerrado**: Finalizado, sin facturación pendiente
- **Facturado**: Cerrado y completamente facturado

---

## Asignación de Personas

### Asignar Persona a Proyecto

1. Ve al detalle del proyecto
2. Click en **+ Asignar Persona**
3. Selecciona:
   - **Persona** a asignar
   - **Rol en el Proyecto**: Líder, Colaborador, Soporte
   - **Horas Estimadas**: Total de horas esperadas
   - **Costo/Hora**: Se usa el costo estándar o se puede sobrescribir
   - **Fecha Inicio**: Cuándo comienza la asignación

### Roles en Proyectos

- **Líder**: Responsable principal (generalmente Socios/Directores)
- **Colaborador**: Ejecutor del proyecto
- **Soporte**: Apoyo puntual

### Validación de Capacidad

El sistema muestra advertencias si:
- La persona está sobre-asignada (>100% capacidad)
- Ya está asignada a muchos proyectos
- No tiene capacidad disponible

---

## Registro de Horas

### Cómo Registrar Horas en un Proyecto

1. Ve a **Horas** → **+ Nueva Hora**
2. Completa:
   - **Persona**: Quien trabajó
   - **Cliente**: Cliente del proyecto
   - **Proyecto**: Proyecto específico (NUEVO)
   - **Fecha**: Cuándo se trabajó
   - **Horas**: Cantidad de horas
   - **Descripción**: Qué se hizo

### Importante

- Ahora el campo **Proyecto** es obligatorio para nuevos registros
- El sistema filtra proyectos según el cliente seleccionado
- Solo se muestran proyectos activos

---

## Análisis de Rentabilidad

### Rentabilidad por Proyecto

**Ruta:** `/proyectos/<id>`

Muestra:
- **Ingresos vs Costos**: En UF y pesos
- **Margen**: Porcentaje de rentabilidad
- **ROI**: Retorno sobre inversión
- **Utilidad Bruta/Neta**: Antes y después de impuestos
- **Equipo**: Distribución de horas por persona
- **Estado**: Óptimo, Aceptable o Bajo

### Comparar Proyectos de un Cliente

**API:** `GET /api/clientes/<cliente_id>/proyectos/comparar`

Retorna:
```json
{
  "cliente": "Banco Nacional",
  "total_proyectos": 3,
  "margen_promedio": 18.5,
  "proyecto_mas_rentable": {
    "nombre": "Campaña Digital",
    "margen": 25.3
  },
  "proyecto_menos_rentable": {
    "nombre": "Crisis Reputacional",
    "margen": 8.2
  }
}
```

### Productividad Persona en Proyecto

**API:** `GET /api/personas/<persona_id>/proyectos/<proyecto_id>/productividad`

Retorna:
```json
{
  "persona": "María González",
  "proyecto": "Campaña Digital 2025",
  "horas_trabajadas": 45.5,
  "porcentaje_participacion": 35.2,
  "margen_generado": 18.3,
  "roi": 42.5,
  "eficiencia": 1.8
}
```

### Proyectos en Riesgo

**API:** `GET /api/proyectos/riesgo`

Identifica proyectos con:
- Margen bajo (< 80% del objetivo)
- Sobre presupuesto (> 110% del presupuestado)
- Con pérdidas (utilidad negativa)

---

## API Endpoints

### Proyectos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/proyectos` | Listar proyectos (filtros: cliente_id, estado, area) |
| `GET` | `/api/proyectos/<id>` | Detalle de proyecto |
| `POST` | `/api/proyectos` | Crear proyecto |
| `GET` | `/api/proyectos/<id>/rentabilidad` | Rentabilidad del proyecto |
| `POST` | `/api/proyectos/<id>/asignar` | Asignar persona |
| `GET` | `/api/proyectos/riesgo` | Proyectos en riesgo |

### Personas y Proyectos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/personas/<id>/proyectos` | Proyectos de una persona |
| `GET` | `/api/personas/<id>/proyectos/<proyecto_id>/productividad` | Productividad en proyecto |

### Clientes y Proyectos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/clientes/<id>/proyectos` | Proyectos de un cliente |
| `GET` | `/api/clientes/<id>/proyectos/comparar` | Comparar rentabilidad |

### Ejemplos de Uso

#### Crear Proyecto

```bash
curl -X POST http://localhost:5000/api/proyectos \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "nombre": "Campaña Redes Sociales Q1",
    "tipo": "permanente",
    "fecha_inicio": "2025-01-01",
    "presupuesto_uf": 250,
    "margen_objetivo": 15
  }'
```

#### Obtener Rentabilidad

```bash
curl http://localhost:5000/api/proyectos/1/rentabilidad
```

#### Comparar Proyectos de Cliente

```bash
curl http://localhost:5000/api/clientes/1/proyectos/comparar
```

#### Asignar Persona a Proyecto

```bash
curl -X POST http://localhost:5000/api/proyectos/1/asignar \
  -H "Content-Type: application/json" \
  -d '{
    "persona_id": 3,
    "rol_proyecto": "lider",
    "horas_estimadas": 80,
    "fecha_inicio": "2025-01-01"
  }'
```

---

## Casos de Uso Comunes

### 1. ¿Qué margen tiene cada proyecto del Cliente X?

```python
import requests

cliente_id = 1
response = requests.get(f'http://localhost:5000/api/clientes/{cliente_id}/proyectos')
proyectos = response.json()

for p in proyectos:
    print(f"{p['nombre']}: {p['margen']}% de margen")
```

### 2. ¿Cuánto aportó María al Proyecto de Crisis?

```python
persona_id = 1
proyecto_id = 5

response = requests.get(
    f'http://localhost:5000/api/personas/{persona_id}/proyectos/{proyecto_id}/productividad'
)
data = response.json()

print(f"Margen generado: {data['margen_generado']} UF")
print(f"ROI: {data['roi']}%")
```

### 3. ¿Qué proyectos están en riesgo?

```python
response = requests.get('http://localhost:5000/api/proyectos/riesgo')
proyectos_riesgo = response.json()

for p in proyectos_riesgo:
    print(f"{p['codigo']}: {', '.join(p['razones'])}")
```

### 4. ¿Puede Juan tomar 20h/mes del nuevo Proyecto B?

```python
# 1. Obtener proyectos actuales de Juan
response = requests.get('http://localhost:5000/api/personas/2/proyectos')
proyectos_juan = response.json()

total_horas = sum(p['horas'] for p in proyectos_juan)
print(f"Juan tiene {total_horas}h comprometidas")

# 2. Calcular capacidad (156h/mes full-time)
capacidad_disponible = 156 - total_horas
print(f"Capacidad disponible: {capacidad_disponible}h")

if capacidad_disponible >= 20:
    print("✅ Juan puede tomar el proyecto")
else:
    print("❌ Juan no tiene capacidad suficiente")
```

---

## Mejores Prácticas

### 1. Organización de Proyectos
- Usa nombres descriptivos: "Campaña Digital Q1 2025" en vez de "Proyecto 1"
- Mantén códigos consistentes
- Actualiza el estado cuando corresponda

### 2. Asignación de Personas
- Verifica capacidad antes de asignar
- Define roles claramente (líder vs colaborador)
- Estima horas realistas

### 3. Registro de Horas
- Registra horas diariamente
- Asocia siempre al proyecto correcto
- Usa descripciones claras

### 4. Seguimiento
- Revisa semanalmente los proyectos en riesgo
- Compara margen real vs objetivo mensualmente
- Analiza productividad por persona trimestralmente

---

## Troubleshooting

### Problema: No veo el campo Proyecto al registrar horas

**Solución:** Asegúrate de haber ejecutado la migración y reiniciado el servidor.

### Problema: Las horas antiguas no tienen proyecto asignado

**Solución:** Ejecuta el script de migración: `python migrate_to_proyectos.py`

### Problema: Error al crear proyecto con código duplicado

**Solución:** Deja el campo código vacío para generación automática, o usa un código único.

### Problema: Rentabilidad del proyecto muestra 0

**Solución:** Verifica que:
- El proyecto tenga horas registradas
- Existan facturas asociadas al proyecto
- Las fechas estén en el rango de análisis

---

## Contacto y Soporte

Para consultas o problemas:
- Revisa los logs en `app.log`
- Consulta la documentación técnica en `README.md`
- Verifica el estado de la base de datos con el script de validación

---

**Última actualización:** Septiembre 2025
**Versión del sistema:** 2.0 (con soporte de Proyectos)
