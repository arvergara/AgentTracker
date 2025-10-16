"""
Script para crear las áreas estándar de Comsulting
"""

from app import app, db, Area, Servicio, Tarea

def crear_areas_iniciales():
    """Crea las áreas iniciales de Comsulting"""

    with app.app_context():
        print("="*80)
        print("CREANDO ÁREAS Y SERVICIOS ESTÁNDAR DE COMSULTING")
        print("="*80)

        # Áreas según Agente_Admin.md
        areas_servicios = {
            "Externas": [
                "Comunicaciones externas",
                "Gestión de Crisis",
                "Talleres de vocería",
                "Monitoreo"
            ],
            "Internas": [
                "Comunicaciones internas"
            ],
            "Asuntos Públicos": [
                "Asuntos Públicos"
            ],
            "Redes Sociales": [
                "Estrategia y gestión de redes",
                "Monitoreo digital"
            ],
            "Diseño": [
                "Diseño",
                "Memorias",
                "Desarrollo web"
            ]
        }

        for area_nombre, servicios in areas_servicios.items():
            # Crear o actualizar área
            area = Area.query.filter_by(nombre=area_nombre).first()
            if not area:
                area = Area(nombre=area_nombre, activo=True)
                db.session.add(area)
                db.session.flush()
                print(f"✓ Área creada: {area_nombre}")
            else:
                print(f"  Área existente: {area_nombre}")

            # Crear servicios
            for servicio_nombre in servicios:
                servicio = Servicio.query.filter_by(
                    area_id=area.id,
                    nombre=servicio_nombre
                ).first()

                if not servicio:
                    servicio = Servicio(
                        area_id=area.id,
                        nombre=servicio_nombre,
                        activo=True
                    )
                    db.session.add(servicio)
                    print(f"    → Servicio creado: {servicio_nombre}")

        db.session.commit()

        # Resumen
        total_areas = Area.query.count()
        total_servicios = Servicio.query.count()

        print("\n" + "="*80)
        print("RESUMEN")
        print("="*80)
        print(f"Total áreas: {total_areas}")
        print(f"Total servicios: {total_servicios}")

        print("\n✓ Áreas y servicios creados exitosamente")
        print("="*80)

if __name__ == '__main__':
    crear_areas_iniciales()
