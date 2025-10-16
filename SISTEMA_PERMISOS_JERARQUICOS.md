# Sistema de Permisos Jerárquicos - AgentTracker

## Descripción General

El sistema implementa un modelo de permisos jerárquico basado en el organigrama de Comsulting Oct 2025. Este sistema controla qué información puede ver cada usuario según su posición en la jerarquía organizacional.

## Reglas de Permisos

### Nivel 1: Administradores (Acceso Total)
**Usuario con `es_admin=True`**

Estos usuarios ven **TODA** la información del sistema sin restricciones:
- Blanca Bulnes (Gerenta General)
- Macarena Puigrredón (Socia Ejecutiva)
- Jazmín Sapunar (Administración y Finanzas)

**Pueden ver**: Todos los usuarios, todos los reportes, todas las métricas.

### Nivel 2: Socios/Directores (Reportes Directos)
**Usuarios con subordinados asignados (campo `subordinados`)**

Estos usuarios solo ven:
1. Su propia información
2. Información de sus **reportes DIRECTOS**

**Ejemplo: Bernardita Ochagavía**
- Puede ver: Carolina Rodríguez, Isidora Bello, Janett Poblete, Rocío Romero, Aranza Fernández
- NO puede ver: Ángeles Pérez (que reporta a Carolina Romero, no a Bernardita)

### Nivel 3: Resto del Equipo (Solo Propia Info)
**Usuarios sin subordinados**

Estos usuarios solo ven:
- Su propia información
- Sus propios registros de horas
- Sus propias métricas de productividad

**Ejemplo: Carolina Rodríguez**
- Puede ver: Solo su propia información
- NO puede ver: Información de otras personas, aunque trabajen en el mismo proyecto

## Estructura de la Base de Datos

### Nuevos Campos en Modelo `Persona`

```python
class Persona(db.Model):
    # ... campos existentes ...

    # Nuevos campos para jerarquía
    es_admin = db.Column(db.Boolean, default=False)  # Admin con acceso total
    reporte_a_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=True)

    # Relaciones
    supervisor = db.relationship('Persona', remote_side=[id], backref='subordinados')
```

## Métodos de Permisos

### `puede_ver_persona(otra_persona_id)`

Determina si el usuario actual puede ver información de otra persona.

```python
persona_actual = Persona.query.get(session['user_id'])
if persona_actual.puede_ver_persona(persona_objetivo_id):
    # Mostrar información
else:
    # Denegar acceso
```

### `obtener_personas_visibles()`

Retorna lista de IDs de todas las personas que el usuario puede ver.

```python
persona_actual = Persona.query.get(session['user_id'])
ids_visibles = persona_actual.obtener_personas_visibles()

# Filtrar consultas
personas = Persona.query.filter(Persona.id.in_(ids_visibles)).all()
```

## Decoradores de Permisos

### `@login_required`
Requiere que el usuario esté logueado. Uso básico para todas las rutas protegidas.

```python
@app.route('/dashboard')
@login_required
def dashboard():
    # ...
```

### `@admin_required`
Requiere que el usuario sea administrador (`es_admin=True`).

```python
@app.route('/admin/configuracion')
@admin_required
def configuracion_admin():
    # Solo Blanca, Macarena, Jazmín
```

### `@puede_ver_persona_required(persona_id_param)`
Verifica que el usuario tenga permisos para ver a otra persona específica.

```python
@app.route('/persona/<int:persona_id>/detalle')
@login_required
@puede_ver_persona_required(persona_id_param='persona_id')
def persona_detalle(persona_id):
    # Solo si tiene permisos sobre persona_id
```

## Jerarquía Organizacional Configurada

### Blanca Bulnes (Admin)
- Josefa Arraztoa
- Sofía Martínez
- Andrés Azócar
- José Manuel Valdivieso

### Macarena Puigrredón (Admin)
- Luisa Mendoza
- Mariela Moyano
- Kaenia Berenguel
- Christian Orrego
- Hernán Díaz
- Pedro Pablo Thies
- Ignacio Diaz
- Francisca Carlino
- Leonardo Pezoa

### Bernardita Ochagavía (Socia)
- Carolina Rodríguez
- Isidora Bello
- Janett Poblete
- Rocío Romero
- Aranza Fernández

### Carolina Romero (Socia)
- Ángeles Pérez
- Constanza Pérez-Cueto
- Victor Guillou
- Enrique Elgueta

### Nicolás Marticorena (Socio)
- Andrea Tapia
- Carla Borja
- Nidia Millahueique
- Pilar Gordillo
- Liliana Cortes

### Isabel Espinoza (Socia)
- Ignacio Echeverría
- Anais Sarmiento

## Inicialización y Configuración

### Script de Inicialización Completa

```bash
python inicializar_sistema_completo.py
```

Este script:
1. Crea/recrea la base de datos con el nuevo esquema
2. Crea todos los usuarios (38 personas)
3. Configura los 3 administradores
4. Asigna relaciones de reporte según organigrama

### Migración de Base de Datos Existente

Si ya tienes una base de datos con usuarios, usa:

```bash
python migrar_jerarquia.py
python configurar_jerarquia_organigrama.py
```

## Ejemplos de Uso

### Ejemplo 1: Filtrar Lista de Personas

```python
@app.route('/personas')
@login_required
def listar_personas():
    persona_actual = Persona.query.get(session['user_id'])
    ids_visibles = persona_actual.obtener_personas_visibles()

    # Solo mostrar personas que puede ver
    personas = Persona.query.filter(
        Persona.id.in_(ids_visibles),
        Persona.activo == True
    ).all()

    return render_template('personas.html', personas=personas)
```

### Ejemplo 2: Ver Detalle de Persona con Validación

```python
@app.route('/persona/<int:persona_id>')
@login_required
def ver_persona(persona_id):
    persona_actual = Persona.query.get(session['user_id'])

    # Verificar permisos
    if not persona_actual.puede_ver_persona(persona_id):
        flash('No tienes permisos para ver esta persona', 'error')
        return redirect(url_for('dashboard'))

    persona = Persona.query.get_or_404(persona_id)
    return render_template('persona_detalle.html', persona=persona)
```

### Ejemplo 3: Reportes de Productividad

```python
@app.route('/reportes/productividad')
@login_required
def reporte_productividad():
    persona_actual = Persona.query.get(session['user_id'])
    ids_visibles = persona_actual.obtener_personas_visibles()

    # Calcular métricas solo para personas visibles
    metricas = calcular_metricas_productividad(ids_visibles)

    return render_template('reporte_productividad.html',
                         metricas=metricas,
                         es_admin=persona_actual.es_admin)
```

## Casos de Prueba

### Caso 1: Admin ve todo
```python
# Login como Blanca Bulnes (bbulnes@comsulting.cl)
ids_visibles = blanca.obtener_personas_visibles()
# Resultado: [1, 2, 3, ..., 38]  # Todos los IDs
```

### Caso 2: Socia ve solo sus reportes directos
```python
# Login como Bernardita Ochagavía (mochagavia@comsulting.cl)
ids_visibles = bernardita.obtener_personas_visibles()
# Resultado: [3, 17, 24, 27, 50, 60]  # Ella + sus 5 subordinados
```

### Caso 3: Usuario regular ve solo su info
```python
# Login como Carolina Rodríguez (crodriguez@comsulting.cl)
ids_visibles = carolina_rod.obtener_personas_visibles()
# Resultado: [17]  # Solo su propio ID
```

## Credenciales de Prueba

**Password para todos**: `comsulting2025`

| Tipo | Email | Descripción |
|------|-------|-------------|
| Admin | bbulnes@comsulting.cl | Ve todo el sistema |
| Admin | mpuigrredon@comsulting.cl | Ve todo el sistema |
| Admin | jsapunar@comsulting.cl | Ve todo el sistema |
| Socia | mochagavia@comsulting.cl | Ve sus 5 subordinados |
| Socia | cromero@comsulting.cl | Ve sus 4 subordinados |
| Usuario | crodriguez@comsulting.cl | Solo ve su info |

## Consideraciones de Seguridad

1. **Validación en Backend**: Siempre validar permisos en el servidor, nunca confiar en el frontend
2. **Filtrado de Consultas**: Usar `obtener_personas_visibles()` para filtrar todas las consultas
3. **Logs de Acceso**: Considerar implementar logs de quién accede a qué información
4. **Actualización de Jerarquía**: Cuando cambie el organigrama, ejecutar `configurar_jerarquia_organigrama.py`

## Mantenimiento

### Agregar Nuevo Usuario
1. Agregar a `crear_usuarios.py` o `inicializar_sistema_completo.py`
2. Ejecutar script de creación
3. Actualizar jerarquía en `configurar_jerarquia_organigrama.py`
4. Ejecutar configuración de jerarquía

### Cambiar Relaciones de Reporte
1. Editar `configurar_jerarquia_organigrama.py`
2. Ejecutar: `python configurar_jerarquia_organigrama.py`

### Promover a Administrador
```python
from app import app, db, Persona

with app.app_context():
    persona = Persona.query.filter_by(email='email@comsulting.cl').first()
    persona.es_admin = True
    db.session.commit()
```

## Próximos Pasos (Opcional)

- [ ] Implementar permisos a nivel de cliente/proyecto
- [ ] Agregar log de auditoría de accesos
- [ ] Notificaciones cuando alguien ve tu información
- [ ] Dashboard específico para cada nivel jerárquico
- [ ] Exportar reportes solo con datos autorizados

---

**Última actualización**: 15 de octubre de 2025
**Versión**: 1.0
**Autor**: Sistema AgentTracker
