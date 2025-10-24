#!/usr/bin/env python3
"""
Verificar ingresos SPOT en base de datos de producción (Render)

Este script se conecta directamente a la base de datos de producción
usando DATABASE_URL de Render.

IMPORTANTE: Debes tener la variable DATABASE_URL configurada
"""

import os
import sys
from sqlalchemy import create_engine, func, distinct, text
from sqlalchemy.orm import sessionmaker

def cargar_env_produccion():
    """Carga DATABASE_URL desde .env.production si existe"""
    env_file = '.env.production'

    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key == 'DATABASE_URL':
                        os.environ['DATABASE_URL'] = value
                        print(f"✓ DATABASE_URL cargado desde {env_file}")
                        return True
    return False

def conectar_produccion():
    """Conecta a la base de datos de producción"""

    # Intentar cargar desde .env.production
    cargar_env_produccion()

    # Intentar obtener DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("❌ No se encontró DATABASE_URL")
        print("\nOpciones:")
        print("1. Crear archivo .env.production:")
        print("   DATABASE_URL=postgresql://...")
        print("\n2. Exportar variable de entorno:")
        print("   export DATABASE_URL='postgresql://...'")
        print("\n3. Pasar como argumento:")
        print("   python verificar_produccion_remote.py 'postgresql://...'")
        print("\n4. Obtener de Render Dashboard:")
        print("   - Ve a tu app en Render")
        print("   - Connections → External Database URL")
        return None

    # Corregir formato de Render (postgres:// → postgresql://)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Test connection
        session.execute(text('SELECT 1'))

        print("✓ Conectado a base de datos de producción")
        return session

    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return None


def analizar_ingresos_spot(session):
    """Analiza ingresos SPOT en producción"""

    print("\n" + "=" * 80)
    print("ANÁLISIS DE INGRESOS SPOT - PRODUCCIÓN")
    print("=" * 80)
    print()

    # 1. Total de clientes por tipo
    print("1. CLIENTES POR TIPO")
    print("-" * 80)

    result = session.execute(text("""
        SELECT tipo, COUNT(*) as total
        FROM clientes
        WHERE activo = true
        GROUP BY tipo
        ORDER BY tipo
    """))

    for tipo, total in result:
        print(f"  {tipo or 'Sin tipo':15s}: {total:3d} clientes")

    # 2. Ingresos totales por tipo de cliente
    print("\n2. INGRESOS TOTALES POR TIPO DE CLIENTE")
    print("-" * 80)

    result = session.execute(text("""
        SELECT
            c.tipo,
            SUM(im.ingreso_uf) as total_ingresos,
            COUNT(DISTINCT c.id) as num_clientes
        FROM clientes c
        JOIN servicios_cliente sc ON c.id = sc.cliente_id
        JOIN ingresos_mensuales im ON sc.id = im.servicio_id
        WHERE c.activo = true AND sc.activo = true
        GROUP BY c.tipo
        ORDER BY c.tipo
    """))

    for tipo, total_ingresos, num_clientes in result:
        print(f"  {tipo or 'Sin tipo':15s}: {total_ingresos:10.2f} UF ({num_clientes} clientes)")

    # 3. Clientes con AMBOS tipos de servicios (permanente y spot)
    print("\n3. CLIENTES CON SERVICIOS PERMANENTES Y SPOT (PROBLEMA)")
    print("-" * 80)

    result = session.execute(text("""
        SELECT
            c.id,
            c.nombre,
            c.tipo as tipo_cliente,
            COUNT(DISTINCT CASE WHEN sc.es_spot = false THEN sc.id END) as servicios_perm,
            COUNT(DISTINCT CASE WHEN sc.es_spot = true THEN sc.id END) as servicios_spot,
            SUM(CASE WHEN sc.es_spot = false THEN im.ingreso_uf ELSE 0 END) as ingresos_perm,
            SUM(CASE WHEN sc.es_spot = true THEN im.ingreso_uf ELSE 0 END) as ingresos_spot
        FROM clientes c
        JOIN servicios_cliente sc ON c.id = sc.cliente_id
        LEFT JOIN ingresos_mensuales im ON sc.id = im.servicio_id
        WHERE c.activo = true AND sc.activo = true
        GROUP BY c.id, c.nombre, c.tipo
        HAVING
            COUNT(DISTINCT CASE WHEN sc.es_spot = false THEN sc.id END) > 0
            AND COUNT(DISTINCT CASE WHEN sc.es_spot = true THEN sc.id END) > 0
        ORDER BY (SUM(CASE WHEN sc.es_spot = false THEN im.ingreso_uf ELSE 0 END) +
                  SUM(CASE WHEN sc.es_spot = true THEN im.ingreso_uf ELSE 0 END)) DESC
    """))

    clientes_problema = list(result)

    if clientes_problema:
        print(f"\n❌ ENCONTRADOS {len(clientes_problema)} CLIENTES CON PROBLEMA:")
        print()

        total_duplicado = 0

        for cliente_id, nombre, tipo_cliente, serv_perm, serv_spot, ing_perm, ing_spot in clientes_problema:
            total = (ing_perm or 0) + (ing_spot or 0)
            total_duplicado += (ing_spot or 0)

            print(f"  • {nombre}")
            print(f"    Tipo en BD: {tipo_cliente}")
            print(f"    Servicios permanentes: {serv_perm}")
            print(f"    Servicios spot: {serv_spot}")
            print(f"    Ingresos permanentes: {ing_perm or 0:.2f} UF")
            print(f"    Ingresos spot (DUPLICADOS): {ing_spot or 0:.2f} UF")
            print(f"    TOTAL SOBREDIMENSIONADO: {total:.2f} UF")
            print()

        print("=" * 80)
        print(f"TOTAL INGRESOS DUPLICADOS: {total_duplicado:.2f} UF")
        print("=" * 80)

    else:
        print("\n✓ No hay clientes con servicios permanentes y spot mezclados")

    # 4. TOP clientes SPOT
    print("\n4. TOP 10 CLIENTES SPOT POR INGRESOS")
    print("-" * 80)

    result = session.execute(text("""
        SELECT
            c.nombre,
            COUNT(DISTINCT sc.id) as num_servicios,
            SUM(im.ingreso_uf) as total_ingresos
        FROM clientes c
        JOIN servicios_cliente sc ON c.id = sc.cliente_id
        JOIN ingresos_mensuales im ON sc.id = im.servicio_id
        WHERE c.tipo = 'spot' AND c.activo = true AND sc.activo = true
        GROUP BY c.id, c.nombre
        ORDER BY SUM(im.ingreso_uf) DESC
        LIMIT 10
    """))

    for nombre, num_servicios, total_ingresos in result:
        marca = "⚠️ " if num_servicios > 1 else "  "
        print(f"{marca} {nombre:40s} {total_ingresos:10.2f} UF (servicios: {num_servicios})")

    # 5. Ingresos SPOT por mes (2024-2025)
    print("\n5. INGRESOS SPOT POR MES (2024-2025)")
    print("-" * 80)

    result = session.execute(text("""
        SELECT
            im.año,
            im.mes,
            SUM(im.ingreso_uf) as total
        FROM clientes c
        JOIN servicios_cliente sc ON c.id = sc.cliente_id
        JOIN ingresos_mensuales im ON sc.id = im.servicio_id
        WHERE c.tipo = 'spot' AND c.activo = true AND sc.activo = true
        GROUP BY im.año, im.mes
        ORDER BY im.año, im.mes
    """))

    meses_nombres = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    año_actual = None
    total_año = 0

    for año, mes, total in result:
        if año_actual != año:
            if año_actual is not None:
                print(f"\n{'TOTAL ' + str(año_actual):15s}: {total_año:10.2f} UF")
                print()
            año_actual = año
            total_año = 0
            print(f"\n{año}:")

        print(f"  {meses_nombres[mes]:12s}: {total:10.2f} UF")
        total_año += total

    if año_actual is not None:
        print(f"\n{'TOTAL ' + str(año_actual):15s}: {total_año:10.2f} UF")

    print("\n")
    return len(clientes_problema) > 0


def main():
    # Intentar obtener DATABASE_URL de argumentos
    if len(sys.argv) > 1:
        os.environ['DATABASE_URL'] = sys.argv[1]

    print("\n╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  VERIFICACIÓN REMOTA - PRODUCCIÓN RENDER".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    # Conectar
    session = conectar_produccion()

    if not session:
        sys.exit(1)

    # Analizar
    tiene_problemas = analizar_ingresos_spot(session)

    # Cerrar conexión
    session.close()

    # Recomendación
    if tiene_problemas:
        print("\n" + "=" * 80)
        print("RECOMENDACIÓN")
        print("=" * 80)
        print()
        print("Se detectaron clientes con servicios PERMANENTES y SPOT mezclados.")
        print()
        print("Próximos pasos:")
        print("1. Ejecutar limpieza en Render Shell:")
        print("   python limpiar_servicios_spot_duplicados.py --ejecutar")
        print()
        print("2. O usar este script modificado para limpiar remotamente")
        print()


if __name__ == '__main__':
    main()
