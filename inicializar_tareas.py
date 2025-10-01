"""
Script para inicializar la base de datos con las tareas predefinidas de Comsulting
Basado en Agente_Admin.md
"""
from app import app, db, Servicio, Tarea

def inicializar_tareas():
    """Crea todas las tareas predefinidas por servicio"""

    # Mapeo de Servicio → Tareas
    tareas_por_servicio = {
        'Comunicaciones Externas': [
            'Alerta AM y PM',
            'Coordinación interna: reuniones equipo, WA, teléfono',
            'Con cliente: Reuniones, WA, teléfono, acta y pauta, VB',
            'Documentos: Redacción, edición y revisión de comunicados, declaraciones, columnas, cartas, relatos, Q&A, etc',
            'Diagnóstico comunicacional: Todo el trabajo que va desde la coordinación de las entrevistas a la entrega de producto final',
            'Estrategia comunicacional: Todo el trabajo que implica desarrollarla y presentarla',
            'Licitaciones: todo el trabajo que implica prepararla hasta presentarla',
            'Gestión de crisis para clientes permanentes',
            'Informe mensual y anual'
        ],
        'Gestión de Crisis': [
            'Solo para clientes de crisis (Isidoro Quiroga por ahora)'
        ],
        'Taller de vocería': [
            'Taller de vocería'
        ],
        'Comunicaciones Internas': [
            'Coordinación interna: reuniones equipo, WA, teléfono',
            'Con cliente: Reuniones, WA, teléfono, acta y pauta, VB',
            'Documentos: Redacción, edición y revisión de relatos, comunicados, avisos, Q&A, newsletters, etc.',
            'Diagnóstico comunicacional: Todo el trabajo que va desde la coordinación de las entrevistas a la entrega de producto final',
            'Estrategia comunicacional: Todo el trabajo que implica desarrollarla y presentarla',
            'Licitaciones: todo el trabajo que implica prepararla hasta presentarla',
            'Informe mensual y anual'
        ],
        'Asuntos Públicos': [
            'Monitoreo legislativo',
            'Coordinación interna: reuniones equipo, WA, teléfono',
            'Con cliente: Reuniones, WA, teléfono, acta y pauta, VB',
            'Con terceros: reuniones, conversaciones con redes',
            'Diagnóstico comunicacional: Todo el trabajo que va desde la coordinación de las entrevistas a la entrega de producto final',
            'Estrategia comunicacional: Todo el trabajo que implica desarrollarla y presentarla',
            'Licitaciones: todo el trabajo que implica prepararla hasta presentarla',
            'Informe mensual y anual'
        ],
        'Monitoreo digital': [
            'Monitoreo digital'
        ],
        'Estrategia y gestión de redes': [
            'Coordinación interna: reuniones equipo, WA, teléfono, coordinación con diseño',
            'Con cliente: Reuniones, WA, teléfono, acta y pauta, VB',
            'Documentos: Redacción, edición y revisión de grillas y de posts',
            'Diagnóstico comunicacional: Todo el trabajo que va desde la coordinación de las entrevistas a la entrega de producto final',
            'Estrategia comunicacional: Todo el trabajo que implica desarrollarla y presentarla',
            'Licitaciones: todo el trabajo que implica prepararla hasta presentarla',
            'Gestión de crisis para clientes permanentes',
            'Informe mensual y anual'
        ],
        'Diseño para comunicaciones internas': [
            'Coordinación interna: reuniones equipo, WA, teléfono, VB',
            'Con cliente: Reuniones, WA, teléfono, acta y pauta, VB',
            'Piezas: desarrollo de piezas gráficas y de video',
            'Licitaciones: todo el trabajo que implica prepararla hasta presentarla',
            'Informes de performance'
        ],
        'Diseño para redes sociales': [
            'Coordinación interna: reuniones equipo, WA, teléfono, VB',
            'Con cliente: Reuniones, WA, teléfono, acta y pauta, VB',
            'Piezas: desarrollo de piezas gráficas y de video',
            'Licitaciones: todo el trabajo que implica prepararla hasta presentarla',
            'Informes de performance'
        ],
        'Diseño para Comsulting': [
            'Coordinación interna: reuniones equipo, WA, teléfono, VB',
            'Con cliente: Reuniones, WA, teléfono, acta y pauta, VB',
            'Piezas: desarrollo de piezas gráficas y de video',
            'Licitaciones: todo el trabajo que implica prepararla hasta presentarla',
            'Informes de performance'
        ],
        'Memorias': [
            'Coordinación interna: reuniones equipo, WA, teléfono, VB',
            'Con cliente: Reuniones, WA, teléfono, acta y pauta, VB',
            'Piezas: desarrollo de piezas gráficas y de video',
            'Licitaciones: todo el trabajo que implica prepararla hasta presentarla',
            'Informes de performance'
        ],
        'Desarrollo web': [
            'Coordinación interna: reuniones equipo, WA, teléfono, VB',
            'Con cliente: Reuniones, WA, teléfono, acta y pauta, VB',
            'Piezas: desarrollo de piezas gráficas y de video',
            'Licitaciones: todo el trabajo que implica prepararla hasta presentarla',
            'Informes de performance'
        ]
    }

    with app.app_context():
        # Verificar si ya existen tareas
        if Tarea.query.count() > 0:
            print(f"⚠️  Ya existen {Tarea.query.count()} tareas en la base de datos.")
            respuesta = input("¿Deseas eliminarlas y crear nuevas? (s/n): ")
            if respuesta.lower() != 's':
                print("❌ Operación cancelada.")
                return

            # Eliminar tareas existentes
            Tarea.query.delete()
            db.session.commit()
            print("🗑️  Tareas existentes eliminadas.")

        print(f"\n📝 Creando tareas...")
        total_tareas = 0

        for servicio_nombre, tareas_lista in tareas_por_servicio.items():
            # Buscar el servicio
            servicio = Servicio.query.filter_by(nombre=servicio_nombre).first()

            if not servicio:
                print(f"  ⚠️  Servicio '{servicio_nombre}' no encontrado. Creando...")
                # Intentar inferir el área del servicio
                area = None
                if 'Comunicaciones Externas' in servicio_nombre or 'Crisis' in servicio_nombre or 'vocería' in servicio_nombre or 'Memorias' in servicio_nombre:
                    area = 'Externas'
                elif 'Comunicaciones Internas' in servicio_nombre:
                    area = 'Internas'
                elif 'Asuntos Públicos' in servicio_nombre:
                    area = 'Asuntos Públicos'
                elif 'Monitoreo' in servicio_nombre or 'redes' in servicio_nombre:
                    area = 'Redes sociales'
                elif 'Diseño' in servicio_nombre or 'web' in servicio_nombre:
                    area = 'Diseño'

                servicio = Servicio(nombre=servicio_nombre, area=area)
                db.session.add(servicio)
                db.session.commit()
                print(f"    ✅ Servicio '{servicio_nombre}' creado (Área: {area})")

            print(f"\n  📋 {servicio_nombre} ({len(tareas_lista)} tarea(s)):")

            for tarea_nombre in tareas_lista:
                tarea = Tarea(nombre=tarea_nombre, servicio_id=servicio.id)
                db.session.add(tarea)
                total_tareas += 1
                # Truncar nombre largo para display
                display_nombre = tarea_nombre if len(tarea_nombre) <= 70 else tarea_nombre[:67] + '...'
                print(f"    ✅ {display_nombre}")

        db.session.commit()
        print(f"\n✨ ¡{total_tareas} tareas creadas exitosamente para {len(tareas_por_servicio)} servicios!\n")

        # Mostrar resumen por área
        print("📊 Resumen por Servicio:")
        servicios = Servicio.query.all()
        for servicio in servicios:
            tareas_count = Tarea.query.filter_by(servicio_id=servicio.id).count()
            print(f"  • {servicio.nombre} ({servicio.area}): {tareas_count} tarea(s)")

if __name__ == '__main__':
    inicializar_tareas()
