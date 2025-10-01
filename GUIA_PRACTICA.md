# 🎯 Guía Práctica: Usando el Sistema de Productividad

## Escenarios Comunes y Cómo Abordarlos

### 📊 Escenario 1: Evaluación Anual de Desempeño

**Situación**: Es diciembre y necesitas decidir aumentos de sueldo y bonos para 2026.

**Pasos a seguir**:

1. **Genera el reporte ejecutivo completo**:
```bash
python analisis_productividad.py
```

2. **Revisa las métricas globales**:
   - ¿La empresa está cumpliendo objetivos? (ROI empresa > 40%)
   - ¿Qué áreas son más rentables?
   - ¿Hay desbalances de carga?

3. **Identifica top performers**:
   - En la aplicación web: ve a "Personas"
   - Para cada persona, haz clic en "📊 Productividad"
   - Busca personas con:
     - ROI > 150%
     - Cumplimiento > 90%
     - Margen > 20%

4. **Toma decisiones**:
   - **Aumentos**: Solo para quienes cumplan las 3 métricas clave
   - **Bonos**: Usa la escala graduada (100%, 75%, 50%, 25%, 0%)
   - **Conversaciones**: Personas con ROI < 80% necesitan feedback

**Resultado esperado**: 
- Decisiones objetivas basadas en datos
- Presupuesto calculado con precisión
- Justificación clara para cada decisión

---

### 👥 Escenario 2: Redistribución de Recursos

**Situación**: Cliente A está creciendo y necesita más recursos. Cliente B está disminuyendo.

**Pasos a seguir**:

1. **Analiza la rentabilidad de ambos clientes**:
   - Web → "Clientes" → Cliente A → "1 Año"
   - Web → "Clientes" → Cliente B → "1 Año"
   - Compara márgenes y ROI

2. **Identifica quién está trabajando en cada cliente**:
   - Web → "Registro de Horas"
   - Filtra por Cliente A y Cliente B
   - Anota las personas involucradas

3. **Revisa la productividad individual en cada cliente**:
   - Web → "Personas" → Ver productividad de cada persona
   - Revisa la sección "Productividad por Proyecto"
   - Identifica quién es más eficiente en cada cliente

4. **Verifica capacidad disponible**:
   - Web → "Dashboard" → "Capacidad Disponible del Equipo"
   - Identifica personas con capacidad libre
   - Personas con <80% utilización pueden tomar más trabajo

5. **Toma la decisión**:
   - Mueve personas eficientes de Cliente B a Cliente A
   - Mantén a los mejores performers en proyectos rentables
   - Considera contratar si nadie tiene capacidad

**Ejemplo práctico**:
```
Cliente A (muy rentable): Necesita +20h/semana
- Ana: 85% utilización, ROI 65% en Cliente A → Asignar +10h
- María: Disponible 15h/semana → Asignar +10h

Cliente B (menos rentable): Reducir 20h/semana
- Pedro: 70% ROI en Cliente B → Reducir a 50% tiempo
- Juan: Mejor en Cliente A → Reasignar completamente
```

---

### 💰 Escenario 3: Cotización de Nuevo Proyecto

**Situación**: Cliente potencial solicita cotización para proyecto de 6 meses.

**Requerimientos del cliente**:
- 20 horas/mes de un Socio
- 40 horas/mes de un Director  
- 80 horas/mes de un Consultor

**Pasos a seguir**:

1. **Verifica si tienes capacidad**:
   - Web → "Dashboard" → "Calculadora de Necesidad de Contratación"
   - Ingresa: 20h Socio, 40h Director, 80h Consultor
   - El sistema te dirá si necesitas contratar

2. **Calcula el precio con margen deseado**:
   - Web → "Dashboard" → "Calculadora de Pricing de Proyectos"
   - Ingresa las mismas horas
   - Prueba con margen 12.5% (objetivo mínimo)
   - Prueba con margen 20% (objetivo ideal)

3. **Analiza el resultado**:

**Ejemplo de salida**:

```
PRECIO CON MARGEN 12.5%:
━━━━━━━━━━━━━━━━━━━━━━━
Costo Total:          280 UF
Precio a Cobrar:      320 UF
Utilidad Bruta:        40 UF
Utilidad Neta:         29 UF (después de impuestos)
Margen Neto:          9.2%

PRECIO CON MARGEN 20%:
━━━━━━━━━━━━━━━━━━━━━━━
Costo Total:          280 UF
Precio a Cobrar:      350 UF
Utilidad Bruta:        70 UF
Utilidad Neta:         51 UF (después de impuestos)
Margen Neto:         14.7%
```

4. **Toma la decisión**:
   - Si tienes capacidad → Cotiza con margen 20%
   - Si estás justo de capacidad → Mínimo 15% margen
   - Si no tienes capacidad y debes contratar → 20-25% margen

5. **Envía la cotización**:
   - Precio mensual: 58.3 UF (350 UF / 6 meses) con margen 20%
   - Valor en pesos: Actualizado según UF del día
   - Desglose de horas por rol

---

### 🚨 Escenario 4: Persona con Bajo Rendimiento

**Situación**: Has notado que Pedro no está rindiendo como esperabas.

**Pasos a seguir**:

1. **Genera el reporte de productividad**:
   - Web → "Personas" → Buscar "Pedro" → "📊 Productividad"

2. **Analiza las métricas**:

**Ejemplo de lo que podrías ver**:
```
PEDRO SILVA - Consultor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Métricas Principales:
├─ ROI Global: 35% ⚠️ (Objetivo: >80%)
├─ Margen: 15 UF
├─ Eficiencia: 1.35x
└─ Cumplimiento: 75% ⚠️ (Objetivo: >85%)

Productividad por Proyecto:
┌─────────────┬───────┬─────┬────────┐
│ Cliente     │ Horas │ ROI │ Margen │
├─────────────┼───────┼─────┼────────┤
│ Cliente A   │ 200h  │ 45% │  8 UF  │
│ Cliente B   │ 150h  │ 25% │  5 UF  │
│ Interno     │  50h  │  0% │ -8 UF  │
└─────────────┴───────┴─────┴────────┘

Recomendaciones:
├─ Aumento: ❌ No
└─ Bono: 0% - Por debajo de expectativas
```

3. **Identifica el problema**:
   - ¿Bajo cumplimiento de horas? (75% vs 100% esperado)
   - ¿Muchas horas en tareas internas no facturables? (50h)
   - ¿ROI bajo en todos los proyectos?

4. **Compara con el equipo**:
   - En el script: `python analisis_productividad.py`
   - Busca el promedio del equipo en ROI y cumplimiento
   - Si Pedro está muy por debajo → Conversación necesaria

5. **Plan de acción**:

**Opción A - Problema de carga**:
```
- Reducir tareas internas (50h → 20h)
- Asignar más trabajo facturable
- Objetivo: 90% cumplimiento en 3 meses
```

**Opción B - Problema de eficiencia**:
```
- Capacitación en áreas débiles
- Mentoring con top performer
- Reasignar a proyectos donde tenga mejor ROI
- Objetivo: ROI >80% en 6 meses
```

**Opción C - Problema de fit**:
```
- Considerar cambio de rol
- Evaluar si el cargo es adecuado
- Plan de mejora de 90 días
```

---

### 📈 Escenario 5: Análisis Trimestral del Área

**Situación**: Como Director del Área de Redes Sociales, quieres evaluar tu área.

**Pasos a seguir**:

1. **Genera el análisis de áreas**:
```bash
python analisis_productividad.py
```

2. **Busca tu área en el reporte**:

**Ejemplo de salida**:
```
📁 Redes sociales
   Personas:      4
   Ingresos:      450.50 UF
   Margen:        135.20 UF (30.0%)
   ROI Promedio:   55.30 %
   Eficiencia:     1.42x
```

3. **Compara con otras áreas**:
```
📁 Externas        → Margen: 35.0%  ROI: 68.5%  🏆 Mejor
📁 Diseño          → Margen: 32.0%  ROI: 62.0%
📁 Redes sociales  → Margen: 30.0%  ROI: 55.3%  ← Tu área
📁 Internas        → Margen: 28.0%  ROI: 48.2%
📁 Asuntos Públicos→ Margen: 25.0%  ROI: 42.0%
```

4. **Identifica oportunidades**:
   - Tu área está en 3er lugar
   - Gap con líder: 5% en margen, 13% en ROI
   - Pregúntate: ¿Por qué Externas es más eficiente?

5. **Drill down en tu equipo**:
   - Web → "Personas" → Filtrar por "Redes sociales"
   - Ver productividad individual de cada uno
   - Identifica al mejor performer de tu área

6. **Acciones**:

**Para mejorar margen**:
```
1. Revisar pricing de servicios (¿estamos cobrando poco?)
2. Reducir costos innecesarios
3. Eliminar trabajo no facturable
4. Buscar clientes más rentables
```

**Para mejorar ROI del equipo**:
```
1. Capacitar al equipo en eficiencia
2. Estandarizar procesos del mejor performer
3. Reasignar trabajo según fortalezas
4. Eliminar cuellos de botella
```

---

## 🎯 Mejores Prácticas

### Para Líderes de Área

✅ **HACER**:
- Revisar productividad del área mensualmente
- Celebrar a los top performers públicamente
- Dar feedback constructivo basado en datos
- Reasignar recursos según eficiencia demostrada
- Compartir mejores prácticas entre el equipo

❌ **NO HACER**:
- Tomar decisiones sin revisar los datos primero
- Comparar personas en diferentes tipos de proyectos sin contexto
- Penalizar por bajo ROI en proyectos estratégicos de largo plazo
- Ignorar el contexto (proyectos nuevos, capacitaciones, etc.)

### Para RH / Dirección

✅ **HACER**:
- Usar el sistema para evaluaciones objetivas
- Proyectar presupuestos de bonos con anticipación
- Identificar necesidades de capacitación
- Detectar desbalances de carga temprano
- Basar aumentos en métricas claras

❌ **NO HACER**:
- Usar el sistema como única herramienta de evaluación (considerar también aspectos cualitativos)
- Tomar decisiones solo en base a un mes de datos
- Ignorar el contexto individual (personal, proyectos especiales, etc.)

### Para Project Managers

✅ **HACER**:
- Asignar personas con buen ROI histórico en el cliente
- Verificar capacidad disponible antes de comprometer
- Monitorear productividad durante el proyecto
- Ajustar asignaciones si hay problemas de eficiencia

❌ **NO HACER**:
- Sobrecargar a los mejores performers (>110% utilización)
- Asignar personas subutilizadas sin entender por qué tienen baja carga
- Ignorar señales de bajo ROI hasta fin de proyecto

---

## 📅 Calendario Recomendado

### Diario
- Registrar horas trabajadas (toda persona)
- Revisar alertas de personas sin registrar horas

### Semanal
- Revisar capacidad del equipo (Lunes)
- Ajustar asignaciones si hay desbalances

### Mensual  
- Generar reporte de productividad por persona
- Analizar rentabilidad de clientes activos
- Identificar proyectos problemáticos

### Trimestral
- Reporte ejecutivo completo
- Análisis comparativo por áreas
- Proyección de bonos
- Decisiones de staffing

### Anual
- Evaluaciones de desempeño
- Decisiones de aumentos (basadas en 12 meses de datos)
- Cálculo y pago de bonos
- Estrategia de recursos para próximo año

---

## 🎓 Tips Finales

1. **Los datos son una herramienta, no la verdad absoluta**: Considera siempre el contexto humano
2. **Tendencias > Snapshots**: 6 meses de datos son más confiables que 1 mes
3. **Comunica transparentemente**: Explica las métricas al equipo
4. **Celebra el éxito**: Reconoce públicamente a los top performers
5. **Sé consistente**: Usa los mismos criterios para todos
6. **Actúa sobre los datos**: No solo midas, toma decisiones basadas en ellos
7. **Itera**: El sistema mejora con feedback del equipo

---

**¿Preguntas sobre cómo usar el sistema? Revisa:**
- `METODOLOGIA_PRODUCTIVIDAD.md` - Explicación detallada de las fórmulas
- `README.md` - Documentación técnica completa
- `INICIO_RAPIDO.md` - Guía de instalación

**¿Necesitas ayuda? El sistema está diseñado para ser intuitivo, pero siempre puedes:**
- Explorar el Dashboard interactivo
- Generar reportes ejecutivos con el script
- Exportar datos para análisis adicional
