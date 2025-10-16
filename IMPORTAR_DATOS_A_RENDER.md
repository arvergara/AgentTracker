# Cómo Importar Datos Históricos a Render

## Problema

La base de datos local tiene 78,853 registros históricos, pero Render no los tiene porque:
1. El archivo CSV (105K líneas) no está en GitHub (excluido por `.gitignore`)
2. SQLite en Render se resetea en cada deploy
3. Los datos solo existen localmente

## Solución: Migrar a PostgreSQL + Importar Datos

### Paso 1: Crear Base de Datos PostgreSQL en Render

1. Ve a https://dashboard.render.com
2. Click en **"New +"** → **"PostgreSQL"**
3. Configuración:
   - **Name**: `agenttracker-db`
   - **Database**: `agenttracker`
   - **User**: (auto-generado)
   - **Region**: Misma que tu web service (Oregon)
   - **PostgreSQL Version**: 15
   - **Plan**: Free (para empezar)

4. Click **"Create Database"**
5. Espera ~2 minutos a que se cree
6. **Copia la "Internal Database URL"** (la que termina en `.render.com`)

### Paso 2: Configurar Web Service para usar PostgreSQL

1. Ve a tu Web Service "AgentTracker" en Render
2. Ve a **"Environment"** en el menú lateral
3. Agrega esta variable:

```
Key: DATABASE_URL
Value: [pega la Internal Database URL de PostgreSQL]
```

4. Click **"Save Changes"**

### Paso 3: Actualizar requirements.txt

Ya está configurado, pero verifica que `requirements.txt` tenga:

```
psycopg2-binary==2.9.9
```

### Paso 4: Actualizar app.py para PostgreSQL

El código ya debería manejar esto, pero verifica que en `app.py` esté:

```python
import os

database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///comsulting_simplified.db'
```

### Paso 5: Re-deploy para Crear Esquema en PostgreSQL

1. En Render → Tu Web Service → Click **"Manual Deploy"** → **"Deploy latest commit"**
2. Espera que el build complete
3. Verifica en logs que se creó el esquema:
   ```
   ✅ Database schema created
   ✅ System initialized successfully
   ```

### Paso 6: Exportar Base de Datos Local a SQL

Desde tu máquina local:

```bash
cd /Users/alfil/Library/CloudStorage/GoogleDrive-andres.vergara@maindset.cl/Mi\ unidad/Comsulting/AgentTracker

# Exportar a SQL
sqlite3 comsulting_simplified.db .dump > agenttracker_backup.sql
```

### Paso 7: Importar a PostgreSQL de Render

**Opción A: Usar Render Shell** (Más fácil pero lento)

1. En Render → Tu Web Service → **"Shell"**
2. Sube el CSV usando el botón de upload o:

```bash
# En tu máquina local, crear un script compacto
cd AgentTracker
python3 << 'EOF'
# Este script crea un SQL con solo los registros de horas
from app import app, db, RegistroHora
import json

with app.app_context():
    registros = RegistroHora.query.limit(1000).all()  # Primeros 1000 para prueba

    inserts = []
    for r in registros:
        inserts.append(f"INSERT INTO registros_horas (persona_id, cliente_id, area_id, servicio_id, tarea_id, fecha, horas, descripcion) VALUES ({r.persona_id}, {r.cliente_id}, {r.area_id}, {r.servicio_id}, {r.tarea_id}, '{r.fecha}', {r.horas}, '{r.descripcion or ''}');")

    with open('insert_horas.sql', 'w') as f:
        f.write('\n'.join(inserts))

    print(f"✓ Creados {len(inserts)} inserts")
EOF
```

**Opción B: Importar CSV Directamente** (Recomendado)

1. Conectarte a PostgreSQL de Render usando la URL externa
2. Ejecutar el script de importación

Desde tu máquina local:

```bash
# Instalar herramienta psql si no la tienes
# brew install postgresql (en Mac)

# Conectar a PostgreSQL de Render
psql "postgresql://[user]:[password]@[host]/[database]"

# Una vez conectado, copiar el CSV (esto requiere el CSV en el servidor)
```

**Opción C: Usar el Script de Importación en Render** (Más Práctico)

Esta es la forma más sencilla:

1. **Crear un backup compacto de solo los datos necesarios**

```bash
cd AgentTracker

# Crear un script que genere un SQL solo con datos
python3 << 'EOF'
from app import app, db
import json

with app.app_context():
    # Exportar todo a JSON
    from app import Cliente, RegistroHora, Area, Servicio, Tarea

    data = {
        'clientes': [{'id': c.id, 'nombre': c.nombre, 'tipo': c.tipo} for c in Cliente.query.all()],
        'areas': [{'id': a.id, 'nombre': a.nombre} for a in Area.query.all()],
        'servicios': [{'id': s.id, 'area_id': s.area_id, 'nombre': s.nombre} for s in Servicio.query.all()],
        'tareas': [{'id': t.id, 'servicio_id': t.servicio_id, 'nombre': t.nombre} for t in Tarea.query.all()],
        'registros': [{
            'persona_id': r.persona_id,
            'cliente_id': r.cliente_id,
            'area_id': r.area_id,
            'servicio_id': r.servicio_id,
            'tarea_id': r.tarea_id,
            'fecha': str(r.fecha),
            'horas': r.horas,
            'descripcion': r.descripcion
        } for r in RegistroHora.query.all()]
    }

    with open('datos_historicos.json', 'w') as f:
        json.dump(data, f)

    print(f"✓ Exportados {len(data['registros'])} registros")
EOF

# Ahora tienes datos_historicos.json con todos los datos
```

2. **Subir el JSON a GitHub** (es más pequeño que el CSV)

```bash
git add datos_historicos.json
git commit -m "feat: Datos históricos para importar en Render"
git push origin main
```

3. **Crear script de importación desde JSON en Render**

Crear `importar_desde_json.py`:

```python
from app import app, db, Cliente, Area, Servicio, Tarea, RegistroHora
import json
from datetime import datetime

def importar_json():
    with app.app_context():
        print("Importando desde JSON...")

        with open('datos_historicos.json', 'r') as f:
            data = json.load(f)

        # Importar en orden
        for c in data['clientes']:
            if not Cliente.query.get(c['id']):
                cliente = Cliente(**c, activo=True)
                db.session.add(cliente)

        db.session.commit()
        print(f"✓ {len(data['clientes'])} clientes")

        # Similar para areas, servicios, tareas, registros
        # ...

        print("✓ Importación completada")

if __name__ == '__main__':
    importar_json()
```

4. **Ejecutar en Render Shell**

```bash
python importar_desde_json.py
```

---

## Opción Más Rápida: Script de Importación Directa

Voy a crear un script optimizado para ti ahora mismo...
