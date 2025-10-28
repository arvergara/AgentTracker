"""
Script de migración: Actualizar de 5 áreas INCORRECTAS a 3 áreas CORRECTAS
Según organigrama oficial de Comsulting

IMPORTANTE: Ejecutar en producción (Render PostgreSQL)
"""

from app import app, db, Area, Servicio, RegistroHora
from sqlalchemy import text

def migrar_areas():
    """Migra de 5 áreas antiguas a 3 áreas correctas"""

    with app.app_context():
        print("\n" + "="*80)
        print("🔄 MIGRACIÓN DE ÁREAS - De 5 a 3 áreas correctas")
        print("="*80 + "\n")

        # 1. Verificar estado actual
        print("📊 PASO 1: Estado actual de la base de datos\n")
        areas_actuales = Area.query.all()
        print(f"Áreas actuales encontradas: {len(areas_actuales)}")
        for area in areas_actuales:
            servicios_count = Servicio.query.filter_by(area_id=area.id).count()
            horas_count = RegistroHora.query.filter_by(area_id=area.id).count()
            print(f"  - {area.nombre}: {servicios_count} servicios, {horas_count} registros de horas")

        # 2. Crear las 3 áreas correctas (si no existen)
        print("\n📝 PASO 2: Creando las 3 áreas correctas...\n")

        areas_nuevas = {
            'Comunicación Externa e Interna': {
                'descripcion': 'Asesoría comunicacional, gestión de crisis, portavocía, comunicaciones internas, relaciones con medios',
                'color': 'rojo'
            },
            'Digital y Diseño': {
                'descripcion': 'Estrategia digital, redes sociales, community management, diseño gráfico, desarrollo web',
                'color': 'verde'
            },
            'Asuntos Públicos': {
                'descripcion': 'Relaciones gubernamentales, asuntos regulatorios, análisis de política pública',
                'color': 'morado'
            }
        }

        areas_map = {}

        for nombre, datos in areas_nuevas.items():
            area_existente = Area.query.filter_by(nombre=nombre).first()
            if area_existente:
                print(f"  ✅ Área '{nombre}' ya existe (ID: {area_existente.id})")
                areas_map[nombre] = area_existente
            else:
                nueva_area = Area(
                    nombre=nombre,
                    descripcion=datos['descripcion'],
                    activo=True
                )
                db.session.add(nueva_area)
                db.session.flush()  # Para obtener el ID
                print(f"  ✅ Área '{nombre}' creada (ID: {nueva_area.id})")
                areas_map[nombre] = nueva_area

        db.session.commit()

        # 3. Mapeo de áreas antiguas a nuevas
        print("\n🔀 PASO 3: Mapeando áreas antiguas a nuevas...\n")

        mapeo_migracion = {
            'Externas': 'Comunicación Externa e Interna',
            'Comunicaciones Externas': 'Comunicación Externa e Interna',
            'Internas': 'Comunicación Externa e Interna',
            'Comunicaciones Internas': 'Comunicación Externa e Interna',
            'Redes sociales': 'Digital y Diseño',
            'Redes Sociales': 'Digital y Diseño',
            'Diseño': 'Digital y Diseño',
            'Digital': 'Digital y Diseño',
            'Asuntos Públicos': 'Asuntos Públicos',
            'Asuntos públicos': 'Asuntos Públicos'
        }

        # 4. Migrar servicios
        print("📦 PASO 4: Migrando servicios a nuevas áreas...\n")

        servicios_migrados = 0
        for area_antigua_nombre, area_nueva_nombre in mapeo_migracion.items():
            area_antigua = Area.query.filter_by(nombre=area_antigua_nombre).first()

            if area_antigua:
                area_nueva = areas_map[area_nueva_nombre]

                # Actualizar servicios
                servicios_a_migrar = Servicio.query.filter_by(area_id=area_antigua.id).all()

                for servicio in servicios_a_migrar:
                    servicio.area_id = area_nueva.id
                    servicios_migrados += 1

                print(f"  ✅ {len(servicios_a_migrar)} servicios migrados de '{area_antigua_nombre}' → '{area_nueva_nombre}'")

        db.session.commit()
        print(f"\n  Total servicios migrados: {servicios_migrados}")

        # 5. Migrar registros de horas
        print("\n⏱️  PASO 5: Migrando registros de horas a nuevas áreas...\n")

        horas_migradas = 0
        for area_antigua_nombre, area_nueva_nombre in mapeo_migracion.items():
            area_antigua = Area.query.filter_by(nombre=area_antigua_nombre).first()

            if area_antigua:
                area_nueva = areas_map[area_nueva_nombre]

                # Actualizar registros de horas
                horas_a_migrar = RegistroHora.query.filter_by(area_id=area_antigua.id).all()

                for registro in horas_a_migrar:
                    registro.area_id = area_nueva.id
                    horas_migradas += 1

                print(f"  ✅ {len(horas_a_migrar)} registros de horas migrados de '{area_antigua_nombre}' → '{area_nueva_nombre}'")

        db.session.commit()
        print(f"\n  Total registros migrados: {horas_migradas}")

        # 6. Marcar áreas antiguas como inactivas
        print("\n🗑️  PASO 6: Marcando áreas antiguas como inactivas...\n")

        areas_a_desactivar = ['Externas', 'Internas', 'Redes sociales', 'Diseño', 'Digital',
                              'Comunicaciones Externas', 'Comunicaciones Internas', 'Redes Sociales']

        for area_nombre in areas_a_desactivar:
            area = Area.query.filter_by(nombre=area_nombre).first()
            if area:
                area.activo = False
                print(f"  ❌ Área '{area_nombre}' marcada como inactiva")

        db.session.commit()

        # 7. Verificar resultado final
        print("\n📊 PASO 7: Verificación final...\n")

        print("Áreas activas después de la migración:")
        areas_activas = Area.query.filter_by(activo=True).all()

        for area in areas_activas:
            servicios_count = Servicio.query.filter_by(area_id=area.id).count()
            horas_count = RegistroHora.query.filter_by(area_id=area.id).count()
            print(f"  ✅ {area.nombre}:")
            print(f"     - Servicios: {servicios_count}")
            print(f"     - Registros de horas: {horas_count}")

        print("\nÁreas inactivas (antiguas):")
        areas_inactivas = Area.query.filter_by(activo=False).all()
        for area in areas_inactivas:
            print(f"  ❌ {area.nombre}")

        print("\n" + "="*80)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*80 + "\n")

        print("📋 RESUMEN:")
        print(f"  - Áreas activas: {len(areas_activas)}")
        print(f"  - Servicios migrados: {servicios_migrados}")
        print(f"  - Registros de horas migrados: {horas_migradas}")
        print(f"  - Áreas antiguas desactivadas: {len(areas_inactivas)}\n")

def rollback_migracion():
    """Rollback en caso de error (solo para emergencias)"""

    with app.app_context():
        print("\n⚠️  EJECUTANDO ROLLBACK...\n")

        # Reactivar áreas antiguas
        areas_antiguas = ['Externas', 'Internas', 'Redes sociales', 'Diseño']
        for area_nombre in areas_antiguas:
            area = Area.query.filter_by(nombre=area_nombre).first()
            if area:
                area.activo = True

        # Desactivar áreas nuevas
        areas_nuevas = ['Comunicación Externa e Interna', 'Digital y Diseño', 'Asuntos Públicos']
        for area_nombre in areas_nuevas:
            area = Area.query.filter_by(nombre=area_nombre).first()
            if area:
                area.activo = False

        db.session.commit()
        print("✅ Rollback completado\n")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        confirm = input("⚠️  ¿Estás seguro de hacer rollback? (yes/no): ")
        if confirm.lower() == 'yes':
            rollback_migracion()
        else:
            print("Rollback cancelado")
    else:
        print("\n⚠️  ADVERTENCIA: Este script modificará la base de datos en producción.")
        print("    Asegúrate de haber hecho un backup antes de continuar.\n")

        confirm = input("¿Deseas continuar con la migración? (yes/no): ")

        if confirm.lower() == 'yes':
            migrar_areas()
        else:
            print("\nMigración cancelada")
