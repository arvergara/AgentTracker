"""
Script para importar el historial de horas 2024-2025 desde Harvest

Este script:
1. Lee el CSV exportado de Harvest
2. Crea/actualiza clientes
3. Crea servicios (considerando el cambio de octubre 2024)
4. Importa todos los registros de horas
5. Asocia registros con personas existentes

IMPORTANTE:
- Antes de octubre 2024: Client y Project tienen el mismo nombre
- Desde octubre 2024: Se separan áreas/servicios del cliente
"""

import csv
from datetime import datetime
from app import app, db, Persona, Cliente, Area, Servicio, Tarea, RegistroHora, ServicioCliente
from decimal import Decimal

# Constantes
FECHA_CAMBIO = datetime(2024, 10, 1)  # Fecha donde cambia la estructura
CSV_PATH = '../Historial2024-2025.csv'

def normalizar_numero(valor_str):
    """Convierte string con coma como decimal a float"""
    if not valor_str or valor_str == '':
        return 0.0
    try:
        # Reemplazar coma por punto
        valor = valor_str.replace(',', '.')
        return float(valor)
    except:
        return 0.0

def buscar_persona_por_nombre(nombre, apellido):
    """Busca una persona por nombre y apellido"""
    # Intentar match exacto
    persona = Persona.query.filter(
        Persona.nombre.ilike(f'%{nombre}%'),
        Persona.nombre.ilike(f'%{apellido}%')
    ).first()

    return persona

def obtener_o_crear_cliente(nombre_cliente):
    """Obtiene o crea un cliente"""
    cliente = Cliente.query.filter_by(nombre=nombre_cliente).first()

    if not cliente:
        # Determinar tipo (permanente por defecto, spot si es "Spot" en el nombre)
        tipo = 'spot' if 'spot' in nombre_cliente.lower() else 'permanente'

        cliente = Cliente(
            nombre=nombre_cliente,
            tipo=tipo,
            activo=True
        )
        db.session.add(cliente)
        db.session.flush()  # Para obtener el ID

    return cliente

def obtener_o_crear_area(nombre_area):
    """Obtiene o crea un área"""
    area = Area.query.filter_by(nombre=nombre_area).first()

    if not area:
        area = Area(nombre=nombre_area, activo=True)
        db.session.add(area)
        db.session.flush()

    return area

def obtener_o_crear_servicio(area, nombre_servicio):
    """Obtiene o crea un servicio dentro de un área"""
    servicio = Servicio.query.filter_by(
        area_id=area.id,
        nombre=nombre_servicio
    ).first()

    if not servicio:
        servicio = Servicio(
            area_id=area.id,
            nombre=nombre_servicio,
            activo=True
        )
        db.session.add(servicio)
        db.session.flush()

    return servicio

def obtener_o_crear_tarea(servicio, nombre_tarea):
    """Obtiene o crea una tarea dentro de un servicio"""
    if not nombre_tarea or nombre_tarea.strip() == '':
        nombre_tarea = 'Tarea general'

    tarea = Tarea.query.filter_by(
        servicio_id=servicio.id,
        nombre=nombre_tarea
    ).first()

    if not tarea:
        tarea = Tarea(
            servicio_id=servicio.id,
            nombre=nombre_tarea,
            activo=True
        )
        db.session.add(tarea)
        db.session.flush()

    return tarea

def determinar_area_por_project(project_nombre):
    """Determina el área basándose en el nombre del proyecto"""
    project_lower = project_nombre.lower()

    if 'rrss' in project_lower or 'social' in project_lower:
        return "Redes Sociales"
    elif 'diseño' in project_lower or 'design' in project_lower:
        return "Diseño"
    elif 'asuntos' in project_lower or 'públicos' in project_lower or 'publicos' in project_lower:
        return "Asuntos Públicos"
    elif 'interna' in project_lower or 'interno' in project_lower:
        return "Internas"
    else:
        return "Externas"

def importar_historial():
    """Importa el historial completo de 2024-2025"""

    with app.app_context():
        print("="*80)
        print("IMPORTACIÓN DE HISTORIAL 2024-2025")
        print("="*80)

        # Contadores
        registros_procesados = 0
        registros_importados = 0
        registros_saltados = 0
        personas_no_encontradas = set()
        clientes_creados = set()
        servicios_creados = set()

        # Leer CSV
        print(f"\nLeyendo CSV: {CSV_PATH}")

        try:
            with open(CSV_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    registros_procesados += 1

                    if registros_procesados % 1000 == 0:
                        print(f"  Procesados: {registros_procesados:,} registros...")
                        db.session.commit()  # Commit periódico

                    try:
                        # Extraer datos
                        fecha_str = row['Date']
                        cliente_nombre = row['Client'].strip()
                        project_nombre = row['Project'].strip()
                        tarea_nombre = row['Task'].strip()
                        nombre = row['First Name'].strip()
                        apellido = row['Last Name'].strip()
                        horas = normalizar_numero(row['Hours'])

                        # Validar datos esenciales
                        if not fecha_str or not cliente_nombre or horas == 0:
                            registros_saltados += 1
                            continue

                        # Parsear fecha
                        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

                        # Buscar persona
                        persona = buscar_persona_por_nombre(nombre, apellido)
                        if not persona:
                            personas_no_encontradas.add(f"{nombre} {apellido}")
                            registros_saltados += 1
                            continue

                        # Obtener/crear cliente
                        cliente = obtener_o_crear_cliente(cliente_nombre)
                        if cliente_nombre not in [c.nombre for c in Cliente.query.all()]:
                            clientes_creados.add(cliente_nombre)

                        # Determinar área y servicio según la fecha
                        if fecha < FECHA_CAMBIO.date():
                            # Antes de octubre 2024: Client y Project son lo mismo
                            # Usar el cliente como nombre del servicio
                            area_nombre = "Comunicaciones"  # Área por defecto
                            servicio_nombre = cliente_nombre
                        else:
                            # Desde octubre 2024: Project indica el servicio/área
                            if project_nombre == '':
                                area_nombre = "Comunicaciones"
                                servicio_nombre = cliente_nombre
                            else:
                                # El project puede indicar el área (RRSS, Diseño, etc.)
                                area_nombre = determinar_area_por_project(project_nombre)
                                servicio_nombre = project_nombre

                        # Obtener/crear área
                        area = obtener_o_crear_area(area_nombre)

                        # Obtener/crear servicio
                        servicio = obtener_o_crear_servicio(area, servicio_nombre)
                        servicio_key = f"{area_nombre}/{servicio_nombre}"
                        if servicio_key not in servicios_creados:
                            servicios_creados.add(servicio_key)

                        # Obtener/crear tarea
                        tarea = obtener_o_crear_tarea(servicio, tarea_nombre)

                        # Crear registro de hora
                        registro = RegistroHora(
                            persona_id=persona.id,
                            cliente_id=cliente.id,
                            area_id=area.id,
                            servicio_id=servicio.id,
                            tarea_id=tarea.id,
                            fecha=fecha,
                            horas=horas,
                            descripcion=row.get('Notes', '')
                        )

                        db.session.add(registro)
                        registros_importados += 1

                    except Exception as e:
                        print(f"\n  ⚠️  Error en línea {registros_procesados}: {e}")
                        registros_saltados += 1
                        continue

                # Commit final
                db.session.commit()

                print("\n" + "="*80)
                print("RESUMEN DE IMPORTACIÓN")
                print("="*80)

                print(f"\n📊 Registros:")
                print(f"  Procesados: {registros_procesados:,}")
                print(f"  Importados: {registros_importados:,}")
                print(f"  Saltados: {registros_saltados:,}")

                print(f"\n🏢 Clientes creados: {len(clientes_creados)}")
                if clientes_creados:
                    for c in sorted(list(clientes_creados))[:10]:
                        print(f"  • {c}")
                    if len(clientes_creados) > 10:
                        print(f"  ... y {len(clientes_creados) - 10} más")

                print(f"\n⚙️  Servicios creados: {len(servicios_creados)}")

                if personas_no_encontradas:
                    print(f"\n⚠️  Personas no encontradas: {len(personas_no_encontradas)}")
                    for p in sorted(list(personas_no_encontradas))[:20]:
                        print(f"  • {p}")
                    if len(personas_no_encontradas) > 20:
                        print(f"  ... y {len(personas_no_encontradas) - 20} más")

                # Estadísticas finales
                total_clientes = Cliente.query.count()
                total_areas = Area.query.count()
                total_servicios = Servicio.query.count()
                total_tareas = Tarea.query.count()
                total_registros = RegistroHora.query.count()

                print(f"\n📈 Totales en base de datos:")
                print(f"  Clientes: {total_clientes}")
                print(f"  Áreas: {total_areas}")
                print(f"  Servicios: {total_servicios}")
                print(f"  Tareas: {total_tareas}")
                print(f"  Registros de horas: {total_registros:,}")

                # Rango de fechas
                primer_registro = RegistroHora.query.order_by(RegistroHora.fecha).first()
                ultimo_registro = RegistroHora.query.order_by(RegistroHora.fecha.desc()).first()

                if primer_registro and ultimo_registro:
                    print(f"\n📅 Rango de fechas:")
                    print(f"  Desde: {primer_registro.fecha}")
                    print(f"  Hasta: {ultimo_registro.fecha}")

                print("\n" + "="*80)
                print("✓ IMPORTACIÓN COMPLETADA")
                print("="*80)

        except FileNotFoundError:
            print(f"\n❌ Error: No se encontró el archivo {CSV_PATH}")
            print(f"Ubicación esperada: {CSV_PATH}")
        except Exception as e:
            print(f"\n❌ Error durante la importación: {e}")
            db.session.rollback()

if __name__ == '__main__':
    importar_historial()
