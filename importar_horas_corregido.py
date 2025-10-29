"""
Script para importar horas desde Excel Historial 2024-2025 con mapeo correcto de nombres

Este script:
1. Crea personas faltantes en la BD
2. Mapea correctamente nombres de Excel (Harvest) a nombres en BD
3. Importa registros de horas asociándolos correctamente a personas y clientes
4. Evita duplicados verificando si el registro ya existe

IMPORTANTE: Solo importa registros de 2025 (ene-sep) que faltan
"""

import pandas as pd
import sqlite3
from datetime import datetime
from collections import defaultdict

# Configuración
EXCEL_PATH = '/Users/alfil/Desktop/Desarrollos/Comsulting/Historial 2024-2025.xlsx'
DB_PATH = 'instance/comsulting_simplified.db'

# Mapeo de nombres: Excel -> BD
MAPEO_NOMBRES = {
    # Mapeo exacto de nombres diferentes
    'Ángeles Pérez': 'María De Los Ángeles Pérez',
    'Andrés Azócar': 'Raúl Andrés Azócar',
    'Nidia Millahueique': 'Juana Nidia Millahueique',

    # Mapeo por acentos/tildes
    'Bernardita Ochagavía': 'María Bernardita Ochagavia',
    'Ignacio Echevería': 'Luis Ignacio Echeverría',
    'Ignacio Díaz': 'Ignacio Diaz',
    'Liliana Cortés': 'Liliana Cortes',
    'Sofía Martinez': 'Sofía Martínez',
    'Víctor Guillou': 'Victor Guillou',
    'Hernan Díaz Diseño': 'Hernán Díaz',

    # Nicolás Campos lo dejamos aparte - verificar si es Marticorena
    'Nicolás Campos': 'Nicolás Campos',  # Se creará como persona nueva
}

# Personas que deben ser creadas (no existen en BD)
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

def crear_personas_faltantes(conn):
    """Crea personas que no existen en la BD"""
    print("\n=== CREANDO PERSONAS FALTANTES ===\n")

    cursor = conn.cursor()
    personas_creadas = 0

    for nombre in PERSONAS_NUEVAS:
        # Verificar si ya existe
        cursor.execute("SELECT id FROM personas WHERE nombre = ?", (nombre,))
        if cursor.fetchone():
            print(f"  ⚠️  {nombre} ya existe, saltando...")
            continue

        # Crear persona con valores por defecto
        cursor.execute("""
            INSERT INTO personas (
                nombre, email, cargo, activo, es_socia, es_admin,
                fecha_ingreso, costo_mensual_empresa
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nombre,
            f"{nombre.lower().replace(' ', '.')}@comsulting.cl",
            'Consultor',  # Cargo por defecto
            True,
            False,
            False,
            datetime.now().date(),
            0  # Se actualizará después con costos reales
        ))

        personas_creadas += 1
        print(f"  ✓ Creada: {nombre}")

    conn.commit()
    print(f"\n  Total personas creadas: {personas_creadas}")
    return personas_creadas

def obtener_mapeo_personas(conn):
    """Obtiene el mapeo de nombres Excel -> ID de persona en BD"""
    cursor = conn.cursor()

    # Obtener todas las personas de la BD
    cursor.execute("SELECT id, nombre FROM personas WHERE activo = 1")
    personas_bd = {nombre: id_persona for id_persona, nombre in cursor.fetchall()}

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
        if nombre not in mapeo.values():
            mapeo[nombre] = id_persona

    return mapeo

def obtener_o_crear_cliente(conn, nombre_cliente):
    """Obtiene o crea un cliente"""
    cursor = conn.cursor()

    # Normalizar nombre
    nombre_cliente = nombre_cliente.strip()

    # Buscar cliente existente
    cursor.execute("SELECT id FROM clientes WHERE nombre = ?", (nombre_cliente,))
    result = cursor.fetchone()

    if result:
        return result[0]

    # Crear cliente nuevo
    tipo = 'spot' if 'spot' in nombre_cliente.lower() else 'permanente'
    cursor.execute("""
        INSERT INTO clientes (nombre, tipo, activo, fecha_inicio)
        VALUES (?, ?, ?, ?)
    """, (nombre_cliente, tipo, True, datetime.now().date()))

    conn.commit()
    return cursor.lastrowid

def mapear_area_excel_a_bd(area_excel):
    """Mapea el área del Excel a un área existente en BD"""
    if not area_excel or pd.isna(area_excel):
        return 'Externas'  # Por defecto

    area_excel = str(area_excel).strip().lower()

    # Mapeo de áreas
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
    else:
        return 'Externas'  # Por defecto

def obtener_o_crear_area(conn, nombre_area):
    """Obtiene o crea un área"""
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM areas WHERE nombre = ?", (nombre_area,))
    result = cursor.fetchone()

    if result:
        return result[0]

    # Crear área
    cursor.execute("INSERT INTO areas (nombre, activo) VALUES (?, ?)", (nombre_area, True))
    conn.commit()
    return cursor.lastrowid

def obtener_o_crear_servicio(conn, area_id, nombre_servicio):
    """Obtiene o crea un servicio dentro de un área"""
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM servicios WHERE area_id = ? AND nombre = ?
    """, (area_id, nombre_servicio))
    result = cursor.fetchone()

    if result:
        return result[0]

    # Crear servicio
    cursor.execute("""
        INSERT INTO servicios (area_id, nombre, activo) VALUES (?, ?, ?)
    """, (area_id, nombre_servicio, True))
    conn.commit()
    return cursor.lastrowid

def obtener_o_crear_tarea(conn, servicio_id, nombre_tarea):
    """Obtiene o crea una tarea dentro de un servicio"""
    cursor = conn.cursor()

    if not nombre_tarea or nombre_tarea.strip() == '':
        nombre_tarea = 'Tarea general'

    cursor.execute("""
        SELECT id FROM tareas WHERE servicio_id = ? AND nombre = ?
    """, (servicio_id, nombre_tarea))
    result = cursor.fetchone()

    if result:
        return result[0]

    # Crear tarea
    cursor.execute("""
        INSERT INTO tareas (servicio_id, nombre, activo) VALUES (?, ?, ?)
    """, (servicio_id, nombre_tarea, True))
    conn.commit()
    return cursor.lastrowid

def verificar_registro_existe(conn, persona_id, cliente_id, fecha, horas):
    """Verifica si un registro ya existe para evitar duplicados"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM registros_horas
        WHERE persona_id = ? AND cliente_id = ? AND fecha = ? AND horas = ?
    """, (persona_id, cliente_id, fecha, horas))
    return cursor.fetchone() is not None

def importar_registros(conn, df_excel, mapeo_personas):
    """Importa registros de horas desde Excel"""
    print("\n=== IMPORTANDO REGISTROS DE HORAS ===\n")

    cursor = conn.cursor()

    # Filtrar solo 2025
    df_excel['Date'] = pd.to_datetime(df_excel['Date'])
    df_2025 = df_excel[(df_excel['Date'] >= '2025-01-01') & (df_excel['Date'] < '2025-10-01')].copy()

    # Crear nombre completo
    df_2025['NombreCompleto'] = df_2025['First Name'] + ' ' + df_2025['Last Name']

    print(f"  Total registros en Excel (2025): {len(df_2025):,}\n")

    registros_importados = 0
    registros_duplicados = 0
    registros_error = 0
    personas_sin_match = set()

    for idx, row in df_2025.iterrows():
        if idx % 5000 == 0 and idx > 0:
            print(f"    Procesados: {idx:,} registros...")
            conn.commit()

        try:
            nombre_completo = row['NombreCompleto']
            cliente_nombre = row['Client'].strip()
            fecha = row['Date'].date()
            horas = float(row['Hours'])

            # Validar datos
            if not cliente_nombre or horas == 0:
                continue

            # Obtener persona_id usando el mapeo
            persona_id = mapeo_personas.get(nombre_completo)

            if not persona_id:
                personas_sin_match.add(nombre_completo)
                registros_error += 1
                continue

            # Obtener o crear cliente
            cliente_id = obtener_o_crear_cliente(conn, cliente_nombre)

            # Obtener área, servicio y tarea
            area_excel = row.get('Area', None)
            nombre_area_bd = mapear_area_excel_a_bd(area_excel)
            area_id = obtener_o_crear_area(conn, nombre_area_bd)

            # Usar Project o Client como nombre del servicio
            project_nombre = row.get('Project', '').strip() if pd.notna(row.get('Project')) else cliente_nombre
            servicio_id = obtener_o_crear_servicio(conn, area_id, project_nombre)

            # Obtener tarea
            tarea_nombre = row.get('Task', 'Tarea general').strip()
            tarea_id = obtener_o_crear_tarea(conn, servicio_id, tarea_nombre)

            # Verificar si ya existe
            if verificar_registro_existe(conn, persona_id, cliente_id, fecha, horas):
                registros_duplicados += 1
                continue

            # Insertar registro
            cursor.execute("""
                INSERT INTO registros_horas (
                    persona_id, cliente_id, area_id, servicio_id, tarea_id,
                    fecha, horas, descripcion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                persona_id,
                cliente_id,
                area_id,
                servicio_id,
                tarea_id,
                fecha,
                horas,
                row.get('Notes', '') or ''
            ))

            registros_importados += 1

        except Exception as e:
            print(f"    ⚠️  Error en fila {idx}: {e}")
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
        for persona in sorted(personas_sin_match):
            print(f"    - {persona}")

    return registros_importados

def verificar_totales(conn):
    """Verifica totales después de la importación"""
    print("\n=== VERIFICACIÓN DE TOTALES ===\n")

    cursor = conn.cursor()

    # Total registros 2025
    cursor.execute("""
        SELECT COUNT(*), SUM(horas)
        FROM registros_horas
        WHERE fecha >= '2025-01-01' AND fecha < '2025-10-01'
    """)
    count, total_horas = cursor.fetchone()

    print(f"  Total registros en BD (2025):  {count:,}")
    print(f"  Total horas en BD (2025):      {total_horas:,.2f}")
    print(f"\n  Objetivo (Excel):              45,750 registros")
    print(f"  Objetivo (Excel):              40,426.83 horas")

    diferencia_registros = count - 45750
    diferencia_horas = total_horas - 40426.83

    print(f"\n  Diferencia registros:          {diferencia_registros:+,}")
    print(f"  Diferencia horas:              {diferencia_horas:+,.2f}")

    if abs(diferencia_horas) < 10:
        print("\n  ✓ ¡Los números cuadran!")
    else:
        print("\n  ⚠️  Aún hay diferencias significativas")

    # Por cliente
    print("\n=== TOP 10 CLIENTES POR HORAS (2025) ===\n")
    cursor.execute("""
        SELECT c.nombre, SUM(r.horas) as total_horas
        FROM registros_horas r
        JOIN clientes c ON r.cliente_id = c.id
        WHERE r.fecha >= '2025-01-01' AND r.fecha < '2025-10-01'
        GROUP BY c.id, c.nombre
        ORDER BY total_horas DESC
        LIMIT 10
    """)

    for nombre, horas in cursor.fetchall():
        print(f"  {nombre:40s} {horas:10.2f} horas")

def main():
    """Función principal"""
    print("="*70)
    print("IMPORTACIÓN DE HORAS CON MAPEO CORRECTO")
    print("="*70)

    # Conectar a BD
    conn = sqlite3.connect(DB_PATH)

    try:
        # 1. Crear personas faltantes
        crear_personas_faltantes(conn)

        # 2. Obtener mapeo de personas
        print("\n=== CREANDO MAPEO DE PERSONAS ===\n")
        mapeo_personas = obtener_mapeo_personas(conn)
        print(f"  Total personas mapeadas: {len(mapeo_personas)}")

        # 3. Leer Excel
        print("\n=== LEYENDO EXCEL ===\n")
        df_excel = pd.read_excel(EXCEL_PATH, sheet_name='Horas')
        print(f"  Total registros en Excel: {len(df_excel):,}")

        # 4. Importar registros
        registros_importados = importar_registros(conn, df_excel, mapeo_personas)

        # 5. Verificar totales
        verificar_totales(conn)

        print("\n" + "="*70)
        print("✓ IMPORTACIÓN COMPLETADA")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    main()
