"""
Script para importar áreas, servicios y tareas de Comsulting
"""
from app import app, db, Area, Servicio, Tarea

def importar_datos():
    """Importa las áreas, servicios y tareas de Comsulting"""

    with app.app_context():
        print("Importando áreas, servicios y tareas...")

        # Limpiar datos existentes
        Tarea.query.delete()
        Servicio.query.delete()
        Area.query.delete()
        db.session.commit()

        # Datos estructurados desde la imagen
        datos = {
            "Externas": {
                "Com Externas": [
                    "Diagnóstico y estrategia comunicacional: Todo el trabajo que va desde la coordinación de las entrevistas a la entrega del producto final.",
                    "Alerta AM y PM, fines de semana.",
                    "Coordinación interna: Reuniones equipo, WA, teléfono, VB",
                    "Trabajo con cliente con cliente: Reuniones, WA, teléfono,VB , salidas a terreno.",
                    "Documentos: Lecturas documentos, redacción, edición y revisión de comunicados, declaraciones, columnas, cartas, relatos, pauta y acta, Q&A, etc.",
                    "Gestión de medios: Coordinación con medios y periodistas",
                    "Informe mensual y anual: Revisión de grafías y elaboración del informe",
                    "Gestión de crisis: (Aquí va todo lo de Isidora Quiroga y todo lo relacionado a una crisis de un cliente permanente)",
                    "Coordinación con proveedores",
                    "Licitaciones: Todo el trabajo que implica preparatoria hasta presentarla."
                ],
                "Taller de vocería": [
                    "Preparación, coordinación, desarrollo, informes de devolución.",
                ]
            },
            "Internas": {
                "Com Internas": [
                    "Diagnóstico y estrategia comunicacional: Todo el trabajo que va desde la coordinación de las entrevistas a la entrega del producto final.",
                    "Coordinación interna: reuniones equipo, WA, teléfono, VB",
                    "Trabajo con cliente con cliente: Reuniones, WA, teléfono, VB , salidas a terreno.",
                    "Documentos: Lectura, redacción, edición y revisión de relatos, comunicados, avisos, Q&A, newsletters, etc.",
                    "Informe mensual y anual: Revisión de grafías y elaboración del informe",
                    "Gestión de crisis: Todo lo relacionado a la gestión de la crisis",
                    "Licitaciones: Todo el trabajo que implica preparatoria hasta presentarla.",
                    "Comsulting: Coordinación socias, reunión socias-clientes reunión mensual, procesos de selección, evaluación de desempeño, etc."
                ]
            },
            "Asuntos Públicos": {
                "Asuntos Públicos": [
                    "Diagnóstico y estrategia comunicacional: Todo el trabajo que va desde la coordinación de las entrevistas a la entrega del producto final.",
                    "Monitoreo regulatorio (legislativa y normativa)",
                    "Coordinación interna: reuniones equipo, WA, teléfono, VB",
                    "Trabajo con cliente con cliente: Reuniones, WA, teléfono, VB , salidas a terreno.",
                    "Documentos: Lectura, mensajes, actas y pautas, mapa de stakeholders, planes de conversaciones y estrategias legislativas, y análisis de entorno político (semanal y mensual),etc.",
                    "Coordinación con terceros: Reuniones, conversaciones con redes, gestiones",
                    "Informe mensual y anual",
                    "Licitaciones: Todo el trabajo que implica preparatoria hasta presentarla.",
                    "Comsulting: Relacionamiento (Icare, AMCham, reuniones, etc)"
                ]
            },
            "Redes Sociales": {
                "Monitoreo digital": [
                    "Monitoreo digital semana y fines de semana"
                ],
                "Estrategia y gestión de redes": [
                    "Diagnóstico y estrategia comunicacional: Todo el trabajo que va desde la coordinación de las entrevistas a la entrega del producto final.",
                    "Coordinación interna: Reuniones equipo, wsp, teléfono, coordinación con diseño",
                    "Trabajo con cliente con cliente: Reuniones, WA, teléfono, acta y pauta, VB, salidas a terreno y presencia en eventos.",
                    "Documentos: Redacción, edición y revisión de grafías y de posts",
                    "Gestión de redes: Publicar, programar, responder usuarios, análisis diarios, inversión",
                    "Coordinación con proveedores",
                    "Informe mensual y anual",
                    "Trabajo fines de semana: subir historias con sus imágenes o videos respectivos.",
                    "Licitaciones:todo el trabajo que implica preparatoria hasta presentarla.",
                    "Gestión de crisis",
                    "Coordinación área: no asociado a un cliente particular",
                    "Comsulting: Todo lo relacionado al IG y LD Comsulting"
                ]
            },
            "Diseño": {
                "Diseño": [
                    "Propuestas creativas: Bench, concepto, lineamientos gráficos, líneas gráficas de campañas, diseño de sitios web)",
                    "Coordinación interna: reuniones equipo, WA, teléfono, VB",
                    "Trabajo con cliente: Reuniones, WA, teléfono, acta y pauta, VB facturación.",
                    "Piezas: desarrollo de piezas gráficas y de video, y de ppts",
                    "Informes diarios, mensuales y anuales",
                    "Coordinación con proveedores o externos (programadores, audiovisuales, productoras, fotógrafos, etc)",
                    "Licitaciones:todo el trabajo que implica preparatoria hasta presentarla.",
                    "Comsulting: todo lo relacionado al IG, LD, ppts Comsulting"
                ],
                "Memorias": [
                    "Propuestas gráficas, desarrollo, reuniones con clientes y proveedores"
                ],
                "Desarrollo web": [
                    "Propuesta: Arquitectura de información, bench, redacción de contenidos, mantención, actualización contenidos, fotos, SE.",
                    "Comsulting: Memoria sitio"
                ]
            }
        }

        # Importar datos
        for area_nombre, servicios in datos.items():
            print(f"\nCreando área: {area_nombre}")
            area = Area(nombre=area_nombre, activo=True)
            db.session.add(area)
            db.session.flush()  # Para obtener el ID

            for servicio_nombre, tareas in servicios.items():
                print(f"  - Creando servicio: {servicio_nombre}")
                servicio = Servicio(
                    area_id=area.id,
                    nombre=servicio_nombre,
                    activo=True
                )
                db.session.add(servicio)
                db.session.flush()  # Para obtener el ID

                for tarea_nombre in tareas:
                    print(f"    • Creando tarea: {tarea_nombre[:50]}...")
                    tarea = Tarea(
                        servicio_id=servicio.id,
                        nombre=tarea_nombre,
                        activo=True
                    )
                    db.session.add(tarea)

        db.session.commit()

        # Resumen
        total_areas = Area.query.count()
        total_servicios = Servicio.query.count()
        total_tareas = Tarea.query.count()

        print("\n" + "="*60)
        print("IMPORTACIÓN COMPLETADA")
        print("="*60)
        print(f"Total áreas creadas: {total_areas}")
        print(f"Total servicios creados: {total_servicios}")
        print(f"Total tareas creadas: {total_tareas}")
        print("="*60)

if __name__ == '__main__':
    importar_datos()
