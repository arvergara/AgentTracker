"""
Script para inicializar la base de datos con los servicios de Comsulting
"""
from app import app, db, Servicio

def inicializar_servicios():
    """Crea los servicios iniciales de Comsulting"""

    servicios = [
        {'nombre': 'Comunicaciones Externas', 'area': 'Externas'},
        {'nombre': 'Gestión de Crisis', 'area': 'Externas'},
        {'nombre': 'Taller de vocería', 'area': 'Externas'},
        {'nombre': 'Comunicaciones Internas', 'area': 'Internas'},
        {'nombre': 'Asuntos Públicos', 'area': 'Asuntos Públicos'},
        {'nombre': 'Monitoreo digital', 'area': 'Redes sociales'},
        {'nombre': 'Estrategia y gestión de redes', 'area': 'Redes sociales'},
        {'nombre': 'Diseño para comunicaciones internas', 'area': 'Diseño'},
        {'nombre': 'Diseño para redes sociales', 'area': 'Diseño'},
        {'nombre': 'Diseño para Comsulting', 'area': 'Diseño'},
        {'nombre': 'Memorias', 'area': 'Externas'},
        {'nombre': 'Desarrollo web', 'area': 'Diseño'},
    ]

    with app.app_context():
        # Verificar si ya existen servicios
        if Servicio.query.count() > 0:
            print(f"⚠️  Ya existen {Servicio.query.count()} servicios en la base de datos.")
            respuesta = input("¿Deseas eliminarlos y crear nuevos? (s/n): ")
            if respuesta.lower() != 's':
                print("❌ Operación cancelada.")
                return

            # Eliminar servicios existentes
            Servicio.query.delete()
            db.session.commit()
            print("🗑️  Servicios existentes eliminados.")

        # Crear servicios
        print(f"\n📝 Creando {len(servicios)} servicios...")
        for servicio_data in servicios:
            servicio = Servicio(**servicio_data)
            db.session.add(servicio)
            print(f"  ✅ {servicio_data['nombre']} (Área: {servicio_data['area']})")

        db.session.commit()
        print(f"\n✨ ¡{len(servicios)} servicios creados exitosamente!\n")

        # Mostrar resumen por área
        print("📊 Resumen por Área:")
        for area in ['Externas', 'Internas', 'Asuntos Públicos', 'Redes sociales', 'Diseño']:
            count = Servicio.query.filter_by(area=area).count()
            print(f"  • {area}: {count} servicio(s)")

if __name__ == '__main__':
    inicializar_servicios()
