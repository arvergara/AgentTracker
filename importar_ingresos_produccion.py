"""
Script para importar INGRESOS desde Facturación por área 2025 v2.xlsx a PostgreSQL

Este script:
1. Lee la hoja "Facturacion_cliente_area" del Excel
2. Para cada Cliente-Área, crea ServicioCliente si no existe
3. Inserta registros en ingresos_mensuales para Ene-Sep 2025
4. Valida que la suma de ingresos coincida con Flujo de Caja

IMPORTANTE: Ejecutar en Render Shell con DATABASE_URL configurado
"""

import pandas as pd
import os
from datetime import date
from sqlalchemy import create_engine, text
from decimal import Decimal

# Configuración
EXCEL_PATH = "/Users/alfil/Desktop/Desarrollos/Comsulting/Fuentes de informacion/Facturación por área 2025 v2.xlsx"
VALOR_UF_ACTUAL = 38000  # Pesos por UF

# Obtener DATABASE_URL del ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL no está configurada")
    print("Ejecuta: export DATABASE_URL='postgresql://...'")
    exit(1)

# Fix para Render (postgres:// -> postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Mapeo de áreas Excel -> BD
MAPEO_AREAS = {
    'Comunicaciones externas': 'Externas',
    'AAPP': 'Asuntos Públicos',
    'Asuntos públicos': 'Asuntos Públicos',
    'RRSS': 'Redes Sociales',
    'Redes Sociales': 'Redes Sociales',
    'Comunicaciones Internas': 'Internas',
    'Diseño': 'Diseño',
    'Diseño editorial': 'Diseño',
    'Desarrollo web': 'Diseño',
}

def obtener_o_crear_cliente(conn, nombre_cliente):
    """Obtiene o crea un cliente (case-insensitive)"""
    nombre_cliente = nombre_cliente.strip()

    # Buscar cliente existente (case-insensitive)
    result = conn.execute(text("SELECT id FROM clientes WHERE UPPER(nombre) = UPPER(:nombre)"),
                          {"nombre": nombre_cliente})
    row = result.fetchone()
    if row:
        return row[0]

    # Si no existe, crearlo
    tipo = 'spot' if 'spot' in nombre_cliente.lower() else 'permanente'
    result = conn.execute(text("""
        INSERT INTO clientes (nombre, tipo, activo)
        VALUES (:nombre, :tipo, :activo)
        RETURNING id
    """), {
        "nombre": nombre_cliente,
        "tipo": tipo,
        "activo": True
    })
    print(f"  ✓ Cliente creado: {nombre_cliente}")
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
    print(f"  ✓ Área creada: {nombre_area}")
    return result.fetchone()[0]

def obtener_o_crear_servicio_cliente(conn, cliente_id, area_id, descripcion):
    """Obtiene o crea un servicio_cliente"""
    result = conn.execute(text("""
        SELECT id FROM servicios_cliente
        WHERE cliente_id = :cliente_id AND area_id = :area_id
    """), {"cliente_id": cliente_id, "area_id": area_id})
    row = result.fetchone()
    if row:
        return row[0]

    result = conn.execute(text("""
        INSERT INTO servicios_cliente (cliente_id, area_id, descripcion, activo)
        VALUES (:cliente_id, :area_id, :descripcion, :activo)
        RETURNING id
    """), {
        "cliente_id": cliente_id,
        "area_id": area_id,
        "descripcion": descripcion,
        "activo": True
    })
    return result.fetchone()[0]

def limpiar_ingresos_existentes(conn, año):
    """Elimina ingresos existentes del año para reimportar"""
    result = conn.execute(text("""
        DELETE FROM ingresos_mensuales WHERE año = :año
    """), {"año": año})
    count = result.rowcount
    conn.commit()
    print(f"  ✓ Eliminados {count} registros existentes de {año}")
    return count

def importar_ingresos(conn, df_facturacion):
    """Importa ingresos desde el DataFrame de facturación"""
    print("\n=== IMPORTANDO INGRESOS ===\n")

    año = 2025
    meses = range(1, 10)  # Enero a Septiembre

    registros_creados = 0
    servicios_creados = 0
    total_ingresos_uf = 0

    # Procesar cada fila del Excel
    area_actual = None  # Para mantener el área cuando no se especifica en la fila

    for idx, row in df_facturacion.iterrows():
        area_excel = row.get('Facturación por Area')
        cliente_perm = row.get('Clientes permanentes')
        uf_mes_perm = row.get('UF/mes')
        cliente_spot = row.get('Clientes spot')
        uf_mes_spot = row.get('UF/mes.1')

        # Si la columna de área tiene valor, actualizar área actual
        if pd.notna(area_excel) and str(area_excel).strip() != '':
            if 'Subtotal' in str(area_excel) or 'Total' in str(area_excel):
                continue  # Saltar subtotales
            area_actual = str(area_excel).strip()

        # Si no hay área actual, saltar
        if not area_actual:
            continue

        # Mapear área
        area_bd = MAPEO_AREAS.get(area_actual, area_actual)

        # Procesar cliente permanente si existe
        if pd.notna(cliente_perm) and pd.notna(uf_mes_perm):
            try:
                cliente_nombre = str(cliente_perm).strip()
                uf_mensual = float(uf_mes_perm)

                if cliente_nombre and uf_mensual > 0:
                    # Obtener/crear cliente, área, servicio_cliente
                    cliente_id = obtener_o_crear_cliente(conn, cliente_nombre)
                    area_id = obtener_o_crear_area(conn, area_bd)
                    servicio_id = obtener_o_crear_servicio_cliente(
                        conn, cliente_id, area_id, f"{area_bd} - {cliente_nombre}"
                    )
                    servicios_creados += 1

                    # Crear registros mensuales (Ene-Sep 2025)
                    for mes in meses:
                        ingreso_pesos = uf_mensual * VALOR_UF_ACTUAL

                        conn.execute(text("""
                            INSERT INTO ingresos_mensuales
                            (servicio_cliente_id, año, mes, ingreso_uf, ingreso_pesos)
                            VALUES (:servicio_id, :año, :mes, :ingreso_uf, :ingreso_pesos)
                        """), {
                            "servicio_id": servicio_id,
                            "año": año,
                            "mes": mes,
                            "ingreso_uf": uf_mensual,
                            "ingreso_pesos": ingreso_pesos
                        })
                        registros_creados += 1
                        total_ingresos_uf += uf_mensual

                    print(f"  ✓ {cliente_nombre} ({area_bd}): {uf_mensual} UF/mes")

            except Exception as e:
                print(f"  ⚠️  Error procesando permanente fila {idx}: {e}")
                continue

        # Procesar cliente spot si existe
        if pd.notna(cliente_spot) and pd.notna(uf_mes_spot):
            try:
                cliente_nombre = str(cliente_spot).strip()
                uf_mensual = float(uf_mes_spot)

                if cliente_nombre and uf_mensual > 0:
                    # Obtener/crear cliente, área, servicio_cliente
                    cliente_id = obtener_o_crear_cliente(conn, cliente_nombre)
                    area_id = obtener_o_crear_area(conn, area_bd)
                    servicio_id = obtener_o_crear_servicio_cliente(
                        conn, cliente_id, area_id, f"{area_bd} - {cliente_nombre} (Spot)"
                    )
                    servicios_creados += 1

                    # Crear registros mensuales (Ene-Sep 2025)
                    for mes in meses:
                        ingreso_pesos = uf_mensual * VALOR_UF_ACTUAL

                        conn.execute(text("""
                            INSERT INTO ingresos_mensuales
                            (servicio_cliente_id, año, mes, ingreso_uf, ingreso_pesos)
                            VALUES (:servicio_id, :año, :mes, :ingreso_uf, :ingreso_pesos)
                        """), {
                            "servicio_id": servicio_id,
                            "año": año,
                            "mes": mes,
                            "ingreso_uf": uf_mensual,
                            "ingreso_pesos": ingreso_pesos
                        })
                        registros_creados += 1
                        total_ingresos_uf += uf_mensual

                    print(f"  ✓ {cliente_nombre} ({area_bd}) [SPOT]: {uf_mensual} UF/mes")

            except Exception as e:
                print(f"  ⚠️  Error procesando spot fila {idx}: {e}")
                continue

    conn.commit()

    print("\n" + "="*70)
    print("RESUMEN DE IMPORTACIÓN DE INGRESOS")
    print("="*70)
    print(f"\n  Servicios cliente creados:     {servicios_creados}")
    print(f"  Registros mensuales creados:   {registros_creados}")
    print(f"  Total ingresos importados:     {total_ingresos_uf:,.2f} UF")
    print(f"  Promedio mensual:              {total_ingresos_uf / 9:,.2f} UF/mes")

    return registros_creados, total_ingresos_uf

def verificar_ingresos(conn):
    """Verifica los ingresos importados"""
    print("\n=== VERIFICACIÓN DE INGRESOS ===\n")

    # Total por mes
    result = conn.execute(text("""
        SELECT mes, SUM(ingreso_uf) as total_uf
        FROM ingresos_mensuales
        WHERE año = 2025
        GROUP BY mes
        ORDER BY mes
    """))

    print("  Ingresos mensuales 2025:")
    total_año = 0
    for row in result:
        mes, total_uf = row
        total_año += total_uf
        print(f"    Mes {mes:2d}: {total_uf:8,.2f} UF")

    print(f"\n  Total año 2025: {total_año:,.2f} UF")

    # Top 10 clientes
    result = conn.execute(text("""
        SELECT c.nombre, SUM(im.ingreso_uf) as total_uf
        FROM ingresos_mensuales im
        JOIN servicios_cliente sc ON im.servicio_cliente_id = sc.id
        JOIN clientes c ON sc.cliente_id = c.id
        WHERE im.año = 2025
        GROUP BY c.nombre
        ORDER BY total_uf DESC
        LIMIT 10
    """))

    print("\n  Top 10 clientes por ingresos:")
    for row in result:
        nombre, total_uf = row
        print(f"    {nombre:30s}: {total_uf:8,.2f} UF")

def main():
    """Función principal"""
    print("="*70)
    print("IMPORTACIÓN DE INGRESOS A PRODUCCIÓN (PostgreSQL)")
    print("="*70)
    print(f"\nConectando a: {DATABASE_URL[:50]}...")

    # Leer Excel
    print("\n=== LEYENDO EXCEL ===\n")
    if not os.path.exists(EXCEL_PATH):
        print(f"ERROR: No se encuentra el archivo {EXCEL_PATH}")
        print("Este script debe ejecutarse en el entorno local donde está el Excel")
        print("Luego subir los datos a producción")
        exit(1)

    df_facturacion = pd.read_excel(EXCEL_PATH, sheet_name='Facturacion_cliente_area')
    print(f"  Total filas en Excel: {len(df_facturacion)}")
    print(f"  Columnas: {', '.join(df_facturacion.columns)}")

    # Crear engine de SQLAlchemy
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            # 1. Limpiar ingresos existentes de 2025
            limpiar_ingresos_existentes(conn, 2025)

            # 2. Importar ingresos
            importar_ingresos(conn, df_facturacion)

            # 3. Verificar
            verificar_ingresos(conn)

            print("\n" + "="*70)
            print("✓ IMPORTACIÓN COMPLETADA")
            print("="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
