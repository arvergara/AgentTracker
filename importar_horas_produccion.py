"""
Script para importar horas a PRODUCCIÓN (PostgreSQL en Render)

Este script:
1. Se conecta a PostgreSQL usando DATABASE_URL
2. Crea personas faltantes
3. Importa registros de horas con mapeo correcto de nombres
4. Evita duplicados

IMPORTANTE: Este script debe ejecutarse en el servidor de Render o con acceso a la BD PostgreSQL
"""

import pandas as pd
import os
from datetime import datetime
from sqlalchemy import create_engine, text
from collections import defaultdict

# Configuración
import sys
# Buscar Excel en el directorio del script o en el directorio padre
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(SCRIPT_DIR, 'Historial 2024-2025.xlsx')

# Si no existe, buscar en directorio padre
if not os.path.exists(EXCEL_PATH):
    EXCEL_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), 'Historial 2024-2025.xlsx')

# Si aún no existe, mostrar error
if not os.path.exists(EXCEL_PATH):
    print(f"ERROR: No se encuentra el archivo Excel")
    print(f"Buscado en: {EXCEL_PATH}")
    sys.exit(1)

# Obtener DATABASE_URL del ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL no está configurada")
    print("Ejecuta: export DATABASE_URL='postgresql://...'")
    exit(1)

# Fix para Render (postgres:// -> postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Mapeo de nombres de personas: Excel -> BD
MAPEO_NOMBRES = {
    'Ángeles Pérez': 'María De Los Ángeles Pérez',
    'Andrés Azócar': 'Raúl Andrés Azócar',
    'Nidia Millahueique': 'Juana Nidia Millahueique',
    'Bernardita Ochagavía': 'María Bernardita Ochagavia',
    'Ignacio Echevería': 'Luis Ignacio Echeverría',
    'Ignacio Díaz': 'Ignacio Diaz',
    'Liliana Cortés': 'Liliana Cortes',
    'Sofía Martinez': 'Sofía Martínez',
    'Víctor Guillou': 'Victor Guillou',
    'Hernan Díaz Diseño': 'Hernán Díaz',
    'Nicolás Campos': 'Nicolás Campos',
}

# Mapeo de nombres de clientes: Excel -> BD
MAPEO_CLIENTES = {
    'CLÍNICAS': 'EBM',
    'FALABELLA': 'Falabella',
    'EMBAJADA ITALIA': 'Embajada de Italia',
}

# Personas que deben ser creadas
PERSONAS_NUEVAS = [
    'María Marañón',
    'Vicente Vera',
    'Catalina Durán',
    'Javiera Flores',
    'Felipe Iglesias',
    'Rosirene Clavero',
    'Belén Castro',
    'Nicolás Campos',
]

def arreglar_secuencias(conn):
    """Arregla las secuencias de PostgreSQL para evitar errores de duplicate key"""
    print("\n=== ARREGLANDO SECUENCIAS DE POSTGRESQL ===\n")

    tablas_con_secuencia = [
        ('personas', 'personas_id_seq'),
        ('clientes', 'clientes_id_seq'),
        ('areas', 'areas_id_seq'),
        ('servicios', 'servicios_id_seq'),
        ('tareas', 'tareas_id_seq'),
        ('registros_horas', 'registros_horas_id_seq'),
    ]

    for tabla, secuencia in tablas_con_secuencia:
        try:
            # Sincronizar secuencia con el máximo ID actual
            conn.execute(text(f"""
                SELECT setval('{secuencia}', (SELECT COALESCE(MAX(id), 1) FROM {tabla}), true)
            """))
            print(f"  ✓ Secuencia '{secuencia}' sincronizada")
        except Exception as e:
            print(f"  ⚠️  No se pudo sincronizar '{secuencia}': {e}")

    conn.commit()
    print("\n  Secuencias arregladas\n")

def crear_personas_faltantes(conn):
    """Crea personas que no existen en la BD"""
    print("\n=== CREANDO PERSONAS FALTANTES ===\n")

    personas_creadas = 0

    for nombre in PERSONAS_NUEVAS:
        # Verificar si ya existe
        result = conn.execute(text("SELECT id FROM personas WHERE nombre = :nombre"), {"nombre": nombre})
        if result.fetchone():
            print(f"  ⚠️  {nombre} ya existe, saltando...")
            continue

        # Crear persona con valores por defecto
        conn.execute(text("""
            INSERT INTO personas (
                nombre, email, cargo, activo, es_socia, es_admin,
                fecha_ingreso, costo_mensual_empresa
            ) VALUES (:nombre, :email, :cargo, :activo, :es_socia, :es_admin, :fecha_ingreso, :costo)
        """), {
            "nombre": nombre,
            "email": f"{nombre.lower().replace(' ', '.')}@comsulting.cl",
            "cargo": 'Consultor',
            "activo": True,
            "es_socia": False,
            "es_admin": False,
            "fecha_ingreso": datetime.now().date(),
            "costo": 0
        })

        personas_creadas += 1
        print(f"  ✓ Creada: {nombre}")

    conn.commit()
    print(f"\n  Total personas creadas: {personas_creadas}")
    return personas_creadas

def obtener_mapeo_personas(conn):
    """Obtiene el mapeo de nombres Excel -> ID de persona en BD"""
    # Obtener todas las personas de la BD
    result = conn.execute(text("SELECT id, nombre FROM personas WHERE activo = true"))
    personas_bd = {nombre: id_persona for id_persona, nombre in result.fetchall()}

    # Crear mapeo Excel -> ID
    mapeo = {}
    for nombre_excel in MAPEO_NOMBRES.keys():
        nombre_bd = MAPEO_NOMBRES[nombre_excel]
        if nombre_bd in personas_bd:
            mapeo[nombre_excel] = personas_bd[nombre_bd]
        else:
            print(f"  ⚠️  WARNING: {nombre_bd} no encontrado en BD")

    # Agregar personas que tienen nombre exacto
    for nombre, id_persona in personas_bd.items():
        if nombre not in [v for v in MAPEO_NOMBRES.values()]:
            mapeo[nombre] = id_persona

    return mapeo

def mapear_area_excel_a_bd(area_excel):
    """Mapea el área del Excel a un área existente en BD

    Áreas en producción: Asuntos Públicos, Comunicaciones, Diseño, Externas, Internas, Redes Sociales
    """
    if not area_excel or pd.isna(area_excel):
        return 'Comunicaciones'  # Por defecto usa Comunicaciones (área general)

    area_excel = str(area_excel).strip().lower()

    if 'externa' in area_excel:
        return 'Externas'
    elif 'interna' in area_excel:
        return 'Internas'
    elif 'asuntos' in area_excel or 'público' in area_excel or 'publico' in area_excel:
        return 'Asuntos Públicos'
    elif 'rrss' in area_excel or 'social' in area_excel or 'redes' in area_excel:
        return 'Redes Sociales'
    elif 'diseño' in area_excel or 'design' in area_excel:
        return 'Diseño'
    elif 'comunicacion' in area_excel:
        return 'Comunicaciones'
    else:
        return 'Comunicaciones'  # Por defecto

def obtener_o_crear_cliente(conn, nombre_cliente):
    """Obtiene o crea un cliente"""
    nombre_cliente = nombre_cliente.strip()

    # Aplicar mapeo de nombres si existe
    nombre_cliente_bd = MAPEO_CLIENTES.get(nombre_cliente, nombre_cliente)

    # Buscar cliente existente (case-insensitive)
    result = conn.execute(text("SELECT id FROM clientes WHERE UPPER(nombre) = UPPER(:nombre)"),
                          {"nombre": nombre_cliente_bd})
    row = result.fetchone()
    if row:
        return row[0]

    # Si no existe, crearlo con el nombre mapeado
    tipo = 'spot' if 'spot' in nombre_cliente_bd.lower() else 'permanente'
    result = conn.execute(text("""
        INSERT INTO clientes (nombre, tipo, activo)
        VALUES (:nombre, :tipo, :activo)
        RETURNING id
    """), {
        "nombre": nombre_cliente_bd,
        "tipo": tipo,
        "activo": True
    })
    return result.fetchone()[0]

def obtener_o_crear_area(conn, nombre_area):
    """Obtiene o crea un área"""
    result = conn.execute(text("SELECT id FROM areas WHERE nombre = :nombre"), {"nombre": nombre_area})
    row = result.fetchone()
    if row:
        return row[0]

    result = conn.execute(text("""
        INSERT INTO areas (nombre, activo) VALUES (:nombre, :activo) RETURNING id
    """), {"nombre": nombre_area, "activo": True})
    return result.fetchone()[0]

def obtener_o_crear_servicio(conn, area_id, nombre_servicio):
    """Obtiene o crea un servicio"""
    result = conn.execute(text("""
        SELECT id FROM servicios WHERE area_id = :area_id AND nombre = :nombre
    """), {"area_id": area_id, "nombre": nombre_servicio})
    row = result.fetchone()
    if row:
        return row[0]

    result = conn.execute(text("""
        INSERT INTO servicios (area_id, nombre, activo)
        VALUES (:area_id, :nombre, :activo) RETURNING id
    """), {"area_id": area_id, "nombre": nombre_servicio, "activo": True})
    return result.fetchone()[0]

def obtener_o_crear_tarea(conn, servicio_id, nombre_tarea):
    """Obtiene o crea una tarea"""
    if not nombre_tarea or nombre_tarea.strip() == '':
        nombre_tarea = 'Tarea general'

    result = conn.execute(text("""
        SELECT id FROM tareas WHERE servicio_id = :servicio_id AND nombre = :nombre
    """), {"servicio_id": servicio_id, "nombre": nombre_tarea})
    row = result.fetchone()
    if row:
        return row[0]

    result = conn.execute(text("""
        INSERT INTO tareas (servicio_id, nombre, activo)
        VALUES (:servicio_id, :nombre, :activo) RETURNING id
    """), {"servicio_id": servicio_id, "nombre": nombre_tarea, "activo": True})
    return result.fetchone()[0]

def verificar_registro_existe(conn, persona_id, cliente_id, fecha, horas):
    """Verifica si un registro ya existe"""
    result = conn.execute(text("""
        SELECT id FROM registros_horas
        WHERE persona_id = :persona_id
          AND cliente_id = :cliente_id
          AND fecha = :fecha
          AND horas = :horas
    """), {
        "persona_id": persona_id,
        "cliente_id": cliente_id,
        "fecha": fecha,
        "horas": horas
    })
    return result.fetchone() is not None

def importar_registros(conn, df_excel, mapeo_personas):
    """Importa registros de horas desde Excel"""
    print("\n=== IMPORTANDO REGISTROS DE HORAS ===\n")

    # Filtrar solo 2025
    df_excel['Date'] = pd.to_datetime(df_excel['Date'])
    df_2025 = df_excel[(df_excel['Date'] >= '2025-01-01') & (df_excel['Date'] < '2025-10-01')].copy()
    df_2025['NombreCompleto'] = df_2025['First Name'] + ' ' + df_2025['Last Name']

    print(f"  Total registros en Excel (2025): {len(df_2025):,}\n")

    registros_importados = 0
    registros_duplicados = 0
    registros_error = 0
    personas_sin_match = set()
    errores_detallados = []

    for idx, row in df_2025.iterrows():
        if idx % 5000 == 0 and idx > 0:
            print(f"    Procesados: {idx:,} registros...")
            conn.commit()

        try:
            nombre_completo = row['NombreCompleto']
            cliente_nombre = row['Client'].strip()
            fecha = row['Date'].date()
            horas = float(row['Hours'])

            if not cliente_nombre or horas == 0:
                continue

            persona_id = mapeo_personas.get(nombre_completo)
            if not persona_id:
                personas_sin_match.add(nombre_completo)
                registros_error += 1
                continue

            cliente_id = obtener_o_crear_cliente(conn, cliente_nombre)

            area_excel = row.get('Area', None)
            nombre_area_bd = mapear_area_excel_a_bd(area_excel)
            area_id = obtener_o_crear_area(conn, nombre_area_bd)

            project_nombre = row.get('Project', '').strip() if pd.notna(row.get('Project')) else cliente_nombre
            servicio_id = obtener_o_crear_servicio(conn, area_id, project_nombre)

            tarea_nombre = row.get('Task', 'Tarea general').strip()
            tarea_id = obtener_o_crear_tarea(conn, servicio_id, tarea_nombre)

            if verificar_registro_existe(conn, persona_id, cliente_id, fecha, horas):
                registros_duplicados += 1
                continue

            conn.execute(text("""
                INSERT INTO registros_horas (
                    persona_id, cliente_id, area_id, servicio_id, tarea_id,
                    fecha, horas, descripcion
                ) VALUES (
                    :persona_id, :cliente_id, :area_id, :servicio_id, :tarea_id,
                    :fecha, :horas, :descripcion
                )
            """), {
                "persona_id": persona_id,
                "cliente_id": cliente_id,
                "area_id": area_id,
                "servicio_id": servicio_id,
                "tarea_id": tarea_id,
                "fecha": fecha,
                "horas": horas,
                "descripcion": row.get('Notes', '') or ''
            })

            registros_importados += 1

        except Exception as e:
            # Si hay error, hacer rollback y continuar
            conn.rollback()
            error_msg = f"Cliente: {row.get('Client', 'N/A')}, Persona: {row.get('NombreCompleto', 'N/A')}"
            errores_detallados.append((idx, str(e), error_msg))
            if len(errores_detallados) <= 10:  # Solo mostrar primeros 10
                print(f"    ⚠️  Error en fila {idx}: {e}")
                print(f"        {error_msg}")
            registros_error += 1
            continue

    conn.commit()

    print("\n" + "="*70)
    print("RESUMEN DE IMPORTACIÓN")
    print("="*70)
    print(f"\n  📊 Registros:")
    print(f"    Total en Excel (2025):     {len(df_2025):,}")
    print(f"    Importados nuevos:         {registros_importados:,}")
    print(f"    Duplicados (ya existían):  {registros_duplicados:,}")
    print(f"    Con errores:               {registros_error:,}")

    if personas_sin_match:
        print(f"\n  ⚠️  Personas sin match ({len(personas_sin_match)}):")
        for persona in sorted(personas_sin_match)[:10]:
            print(f"    - {persona}")

    if errores_detallados and len(errores_detallados) > 10:
        print(f"\n  ⚠️  Total de errores SQL: {len(errores_detallados)}")
        print(f"      (Se mostraron solo los primeros 10 arriba)")

    return registros_importados

def verificar_totales(conn):
    """Verifica totales después de la importación"""
    print("\n=== VERIFICACIÓN DE TOTALES ===\n")

    result = conn.execute(text("""
        SELECT COUNT(*), SUM(horas)
        FROM registros_horas
        WHERE fecha >= '2025-01-01' AND fecha < '2025-10-01'
    """))
    count, total_horas = result.fetchone()

    print(f"  Total registros en BD (2025):  {count:,}")
    print(f"  Total horas en BD (2025):      {total_horas:,.2f}")
    print(f"\n  Objetivo (Excel):              45,750 registros")
    print(f"  Objetivo (Excel):              40,426.83 horas")

    diferencia_horas = total_horas - 40426.83
    print(f"\n  Diferencia horas:              {diferencia_horas:+,.2f} ({(diferencia_horas/40426.83*100):+.1f}%)")

    if abs(diferencia_horas) < 100:
        print("\n  ✓ ¡Los números cuadran!")
    else:
        print("\n  ⚠️  Aún hay diferencias")

def main():
    """Función principal"""
    print("="*70)
    print("IMPORTACIÓN DE HORAS A PRODUCCIÓN (PostgreSQL)")
    print("="*70)
    print(f"\nConectando a: {DATABASE_URL[:50]}...")

    # Crear engine de SQLAlchemy
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            # 0. Arreglar secuencias de PostgreSQL
            arreglar_secuencias(conn)

            # 1. Crear personas faltantes
            crear_personas_faltantes(conn)

            # 2. Obtener mapeo
            print("\n=== CREANDO MAPEO DE PERSONAS ===\n")
            mapeo_personas = obtener_mapeo_personas(conn)
            print(f"  Total personas mapeadas: {len(mapeo_personas)}")

            # 3. Leer Excel
            print("\n=== LEYENDO EXCEL ===\n")
            df_excel = pd.read_excel(EXCEL_PATH, sheet_name='Horas')
            print(f"  Total registros en Excel: {len(df_excel):,}")

            # 4. Importar registros
            importar_registros(conn, df_excel, mapeo_personas)

            # 5. Verificar totales
            verificar_totales(conn)

            print("\n" + "="*70)
            print("✓ IMPORTACIÓN COMPLETADA")
            print("="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
