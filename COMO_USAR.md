# 🚀 Cómo Usar AgentTracker - Guía Rápida

## ▶️ Iniciar la Aplicación

```bash
cd "/Users/alfil/Library/CloudStorage/GoogleDrive-andres.vergara@maindset.cl/Mi unidad/Comsulting/AgentTracker"
python3 app.py
```

La aplicación estará disponible en: **http://localhost:5000**

---

## 📋 Datos de Prueba Cargados

La aplicación viene con datos de prueba realistas:

- ✅ **20 Personas** (periodistas y equipo de Comsulting)
- ✅ **10 Clientes** (Banco Nacional, Minera del Norte, Retail Plus, etc.)
- ✅ **18 Proyectos** activos
- ✅ **62 Asignaciones** persona-proyecto
- ✅ **16,914 horas** registradas
- ✅ **51 Facturas** (159 millones de pesos)

---

## 🎯 Funcionalidades Principales

### 1️⃣ Gestionar Personas (Periodistas)

**Ver todas las personas:**
- Ve a: http://localhost:5000/personas
- Verás la lista de 20 periodistas y equipo

**Agregar nueva persona:**
- Click en "➕ Nueva Persona"
- Completa: Nombre, Email, Cargo, Área, Tipo Jornada, Costo/Hora
- Ejemplos de cargos: Socia, Director, Consultor Senior, Analista, Designer
- Áreas: Externas, Internas, Asuntos Públicos, Redes sociales, Diseño

**Editar persona:**
- En la lista, click en "✏️" junto al nombre
- Modifica los datos necesarios
- Guarda cambios

**Eliminar persona:**
- Click en "🗑️" (desactiva, no elimina permanentemente)

---

### 2️⃣ Gestionar Clientes

**Ver todos los clientes:**
- Ve a: http://localhost:5000/clientes

**Agregar nuevo cliente:**
- Click en "➕ Nuevo Cliente"
- Completa: Nombre, Tipo (Permanente/Spot), Área, Fecha Inicio

**Editar cliente:**
- Click en "✏️" junto al cliente
- Modifica los datos
- Guarda

---

### 3️⃣ Gestionar Proyectos

**Ver todos los proyectos:**
- Ve a: http://localhost:5000/proyectos
- Usa filtros por estado (Activo, Pausado, Cerrado)
- Busca por nombre o código

**Crear nuevo proyecto:**
1. Click en "➕ Nuevo Proyecto"
2. Selecciona el **Cliente**
3. Ingresa **Nombre del Proyecto** (ej: "Campaña Digital Q1 2025")
4. El **código se genera automáticamente** (o puedes poner uno personalizado)
5. Selecciona **Servicio** (opcional)
6. Define **Tipo** (Permanente/Spot/Interno)
7. Ingresa **Fechas** de inicio y fin
8. Define **Presupuesto en UF**
9. Establece **Margen Objetivo** (por defecto 12.5%)
10. Guarda

**Editar proyecto:**
- En la lista, click en "✏️"
- O en el detalle del proyecto, click en "✏️ Editar Proyecto"
- Modifica lo necesario (excepto el cliente)

**Ver detalle y rentabilidad:**
- Click en "📊" en la lista
- Verás:
  - Información del proyecto
  - **Rentabilidad**: Ingresos, Costos, Margen, ROI
  - **Equipo asignado** con distribución de horas
  - **Utilidad bruta y neta**

---

### 4️⃣ Asignar Personas a Proyectos

**Desde el proyecto:**
1. Ve al detalle del proyecto (click en 📊)
2. En la sección "Equipo del Proyecto", click en "➕ Asignar Persona"
3. Selecciona la **Persona**
4. Define el **Rol**:
   - **Líder**: Responsable principal (Socios/Directores)
   - **Colaborador**: Ejecutor del proyecto
   - **Soporte**: Apoyo puntual
5. Ingresa **Horas Estimadas** totales para el proyecto
6. El **Costo/Hora** se toma automáticamente (o puedes sobrescribirlo)
7. Define **Fecha de Inicio**
8. Guarda

**Importante:**
- Una persona puede estar asignada a **múltiples proyectos**
- Un proyecto puede tener **múltiples personas**

**Desasignar persona:**
- En el detalle del proyecto, en la tabla de equipo
- Click en "🗑️" junto a la persona
- Confirma

---

### 5️⃣ Registrar Horas por Proyecto

**Registrar horas trabajadas:**
1. Ve a: http://localhost:5000/horas
2. Click en "➕ Nueva Hora"
3. Selecciona:
   - **Persona** que trabajó
   - **Cliente**
   - **Proyecto** (se filtra según el cliente seleccionado) ⭐ NUEVO
   - **Fecha**
   - **Cantidad de horas**
   - **Descripción** (opcional)
4. Guarda

**Importante:** Ahora el registro de horas está asociado a un **proyecto específico**, no solo al cliente.

---

### 6️⃣ Ver Rentabilidad y Análisis

**Rentabilidad por proyecto:**
- Ve al detalle de cualquier proyecto
- Verás automáticamente:
  - Ingresos vs Costos (en UF y pesos)
  - **Margen %** vs Margen Objetivo
  - **ROI** del proyecto
  - Utilidad bruta y neta (antes/después de impuestos)
  - Distribución de horas por persona

**Comparar proyectos de un cliente:**
- API: `GET /api/clientes/<cliente_id>/proyectos/comparar`
- Muestra qué proyecto es más/menos rentable

**Ver proyectos de una persona:**
- API: `GET /api/personas/<persona_id>/proyectos`
- Lista todos los proyectos donde participa

**Productividad persona en proyecto específico:**
- API: `GET /api/personas/<persona_id>/proyectos/<proyecto_id>/productividad`
- ROI individual, margen generado, eficiencia

---

## 🎨 Interfaz

### Navegación Principal

```
┌─────────────────────────────────────────────────┐
│ Comsulting Admin                                │
│ Dashboard | Personas | Clientes | Proyectos | Horas │
└─────────────────────────────────────────────────┘
```

### Colores y Estados

**Estados de Proyectos:**
- 🟢 **Verde (Activo)**: Proyecto en ejecución
- 🟡 **Amarillo (Pausado)**: Temporalmente detenido
- ⚫ **Gris (Cerrado)**: Finalizado
- 🔵 **Azul (Facturado)**: Cerrado y facturado

**Roles en Proyectos:**
- 🔵 **Azul (Líder)**: Responsable principal
- 🔷 **Cyan (Colaborador)**: Ejecutor
- ⚫ **Gris (Soporte)**: Apoyo puntual

---

## 📊 Ejemplos de Uso Práctico

### Ejemplo 1: Crear un Nuevo Proyecto para un Cliente Existente

```
Escenario: Banco Nacional necesita una nueva campaña de redes sociales

1. Ve a /proyectos/nuevo
2. Cliente: "Banco Nacional"
3. Nombre: "Campaña Redes Sociales Q4 2025"
4. Código: (se genera automático: BAN-01-01)
5. Servicio: "Estrategia y gestión de redes"
6. Tipo: Permanente
7. Estado: Activo
8. Fecha inicio: 01/10/2025
9. Fecha fin: 31/12/2025
10. Presupuesto: 300 UF
11. Margen objetivo: 18%
12. Guarda

→ Proyecto creado exitosamente
```

### Ejemplo 2: Asignar Equipo al Proyecto

```
1. Ve al proyecto recién creado
2. Click en "➕ Asignar Persona"

Primera asignación (Líder):
- Persona: Patricia Mendoza (Directora Redes Sociales)
- Rol: Líder
- Horas estimadas: 80h
- Fecha inicio: 01/10/2025
- Guarda

Segunda asignación (Colaborador):
- Persona: Francisca Ramírez (Consultora Redes Sociales)
- Rol: Colaborador
- Horas estimadas: 150h
- Guarda

Tercera asignación (Soporte - Diseño):
- Persona: Camila Espinoza (Designer)
- Rol: Soporte
- Horas estimadas: 40h
- Guarda

→ Equipo asignado: 3 personas, 270 horas totales
```

### Ejemplo 3: Registrar Horas del Equipo

```
1. Ve a /horas/nueva
2. Persona: Patricia Mendoza
3. Cliente: Banco Nacional
4. Proyecto: Campaña Redes Sociales Q4 2025 ⭐
5. Fecha: 01/10/2025
6. Horas: 6
7. Descripción: "Reunión de kickoff con cliente y planning estratégico"
8. Guarda

→ Horas registradas en el proyecto específico
```

### Ejemplo 4: Ver Rentabilidad

```
1. Ve al proyecto "Campaña Redes Sociales Q4 2025"
2. Revisa la sección de Rentabilidad:

📊 Rentabilidad:
- Ingresos: 300 UF ($11,250,000)
- Costos: 250 UF ($9,375,000)
- Margen: 16.7% (vs objetivo 18%)
- ROI: 20%
- Estado: Aceptable (cerca del objetivo)

👥 Equipo:
- Patricia: 80h (30%)
- Francisca: 150h (55%)
- Camila: 40h (15%)
```

---

## 🔍 Preguntas Frecuentes

**Q: ¿Puedo tener a la misma persona en varios proyectos?**
✅ Sí! Una persona puede estar asignada a todos los proyectos que necesites.

**Q: ¿Puedo cambiar el cliente de un proyecto después de crearlo?**
❌ No. El cliente queda fijo al crear el proyecto. Debes crear un nuevo proyecto si necesitas otro cliente.

**Q: ¿Cómo sé si una persona tiene capacidad disponible?**
📊 Ve a `/api/personas/<id>/proyectos` para ver todos sus proyectos actuales.

**Q: ¿Puedo eliminar un proyecto?**
⚠️ Por ahora solo puedes cambiar su estado a "Cerrado". La eliminación completa no está implementada (para preservar historial).

**Q: ¿Qué pasa si desasigno a alguien de un proyecto?**
⚠️ Se desactiva la asignación, pero las horas registradas se mantienen (para historial).

**Q: ¿Cómo calcula el margen?**
💡 Margen = (Ingresos - Costos) / Ingresos × 100

**Q: ¿Cómo se prorratean los ingresos por persona?**
💡 Según su % de participación en los costos del proyecto. Si una persona representa el 30% de los costos, recibe crédito por el 30% de los ingresos.

---

## 🛠️ Comandos Útiles

**Iniciar aplicación:**
```bash
python3 app.py
```

**Regenerar datos de prueba:**
```bash
python3 generar_datos_prueba.py
```

**Ver estructura de archivos:**
```bash
tree -L 2
```

**Backup de la base de datos:**
```bash
cp comsulting.db backup_$(date +%Y%m%d).db
```

---

## 📞 Ayuda

Si encuentras algún problema:
1. Revisa la consola donde corre `python3 app.py` para ver errores
2. Verifica que estés en la URL correcta: http://localhost:5000
3. Asegúrate de que la base de datos `comsulting.db` exista

---

## ✨ Tips y Mejores Prácticas

1. **Nombres descriptivos**: Usa nombres claros para proyectos (ej: "Campaña Digital Q1 2025" en vez de "Proyecto 1")

2. **Códigos únicos**: Deja que el sistema genere los códigos automáticamente para evitar duplicados

3. **Asigna antes de registrar horas**: Asigna a las personas al proyecto antes de que empiecen a registrar horas

4. **Revisa rentabilidad periódicamente**: Revisa el margen de los proyectos semanalmente

5. **Estados claros**: Actualiza el estado del proyecto cuando cambie (activo → pausado → cerrado → facturado)

6. **Presupuestos realistas**: Define presupuestos basados en horas estimadas × costo promedio del equipo

---

**¡Listo para usar! 🚀**

La aplicación está corriendo en: **http://localhost:5000**
