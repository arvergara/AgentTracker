"""
Script para importar datos desde JSON en Render
Ejecutar en Render Shell después de subir datos_historicos.json
"""

from app import app, db
from app import Cliente, Area, Servicio, Tarea, RegistroHora
import json
from datetime import datetime

def importar_datos():
    """Importa datos desde JSON"""

    with app.app_context():
        print("="*80)
        print("IMPORTANDO DATOS DESDE JSON")
        print("="*80)

        try:
            with open('datos_historicos.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"\n📄 Archivo cargado exitosamente")
            print(f"  • Clientes: {len(data['clientes'])}")
            print(f"  • Áreas: {len(data['areas'])}")
            print(f"  • Servicios: {len(data['servicios'])}")
            print(f"  • Tareas: {len(data['tareas'])}")
            print(f"  • Registros: {len(data['registros_horas']):,}")

            # Importar clientes
            print("\n🏢 Importando clientes...")
            for item in data['clientes']:
                cliente = Cliente.query.get(item['id'])
                if not cliente:
                    cliente = Cliente(
                        id=item['id'],
                        nombre=item['nombre'],
                        tipo=item['tipo'],
                        activo=item['activo']
                    )
                    db.session.add(cliente)
            db.session.commit()
            print(f"✓ {len(data['clientes'])} clientes importados")

            # Importar áreas
            print("\n📂 Importando áreas...")
            for item in data['areas']:
                area = Area.query.get(item['id'])
                if not area:
                    area = Area(
                        id=item['id'],
                        nombre=item['nombre'],
                        activo=item['activo']
                    )
                    db.session.add(area)
            db.session.commit()
            print(f"✓ {len(data['areas'])} áreas importadas")

            # Importar servicios
            print("\n⚙️  Importando servicios...")
            for item in data['servicios']:
                servicio = Servicio.query.get(item['id'])
                if not servicio:
                    servicio = Servicio(
                        id=item['id'],
                        area_id=item['area_id'],
                        nombre=item['nombre'],
                        activo=item['activo']
                    )
                    db.session.add(servicio)
            db.session.commit()
            print(f"✓ {len(data['servicios'])} servicios importados")

            # Importar tareas
            print("\n📋 Importando tareas...")
            for item in data['tareas']:
                tarea = Tarea.query.get(item['id'])
                if not tarea:
                    tarea = Tarea(
                        id=item['id'],
                        servicio_id=item['servicio_id'],
                        nombre=item['nombre'],
                        activo=item['activo']
                    )
                    db.session.add(tarea)
            db.session.commit()
            print(f"✓ {len(data['tareas'])} tareas importadas")

            # Importar registros de horas
            print("\n⏰ Importando registros de horas...")
            total = len(data['registros_horas'])
            print(f"  Total a importar: {total:,} registros")

            # Verificar si ya hay registros
            existing = RegistroHora.query.count()
            if existing > 0:
                print(f"\n⚠️  Ya existen {existing:,} registros en la base de datos")
                respuesta = input("¿Deseas eliminarlos y reimportar? (s/n): ")
                if respuesta.lower() == 's':
                    print("  Eliminando registros existentes...")
                    RegistroHora.query.delete()
                    db.session.commit()
                else:
                    print("  Saltando importación de registros de horas")
                    return

            count = 0
            batch_size = 1000
            batch = []

            for item in data['registros_horas']:
                registro = RegistroHora(
                    persona_id=item['persona_id'],
                    cliente_id=item['cliente_id'],
                    area_id=item['area_id'],
                    servicio_id=item['servicio_id'],
                    tarea_id=item['tarea_id'],
                    fecha=datetime.strptime(item['fecha'], '%Y-%m-%d').date(),
                    horas=item['horas'],
                    descripcion=item['descripcion']
                )
                batch.append(registro)
                count += 1

                # Commit cada 1000 registros
                if len(batch) >= batch_size:
                    db.session.bulk_save_objects(batch)
                    db.session.commit()
                    batch = []
                    if count % 10000 == 0:
                        print(f"  Importados: {count:,}/{total:,} registros ({count/total*100:.1f}%)")

            # Commit final
            if batch:
                db.session.bulk_save_objects(batch)
                db.session.commit()

            print(f"✓ {count:,} registros de horas importados")

            # Verificación final
            print("\n" + "="*80)
            print("VERIFICACIÓN FINAL")
            print("="*80)

            total_clientes = Cliente.query.count()
            total_areas = Area.query.count()
            total_servicios = Servicio.query.count()
            total_tareas = Tarea.query.count()
            total_registros = RegistroHora.query.count()

            print(f"\n📊 Totales en base de datos:")
            print(f"  • Clientes: {total_clientes}")
            print(f"  • Áreas: {total_areas}")
            print(f"  • Servicios: {total_servicios}")
            print(f"  • Tareas: {total_tareas}")
            print(f"  • Registros de horas: {total_registros:,}")

            # Rango de fechas
            from sqlalchemy import func
            primer_registro = RegistroHora.query.order_by(RegistroHora.fecha).first()
            ultimo_registro = RegistroHora.query.order_by(RegistroHora.fecha.desc()).first()

            if primer_registro and ultimo_registro:
                print(f"\n📅 Rango de fechas:")
                print(f"  Desde: {primer_registro.fecha}")
                print(f"  Hasta: {ultimo_registro.fecha}")

            total_horas = db.session.query(func.sum(RegistroHora.horas)).scalar() or 0
            print(f"\n⏱️  Total de horas: {total_horas:,.1f}")

            print("\n" + "="*80)
            print("✓ IMPORTACIÓN COMPLETADA EXITOSAMENTE")
            print("="*80)

        except FileNotFoundError:
            print("\n❌ Error: No se encontró el archivo 'datos_historicos.json'")
            print("Asegúrate de que el archivo esté en el directorio actual")
        except Exception as e:
            print(f"\n❌ Error durante la importación: {e}")
            db.session.rollback()

if __name__ == '__main__':
    importar_datos()
