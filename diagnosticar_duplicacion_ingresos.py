#!/usr/bin/env python3
"""
Diagnosticar duplicación de ingresos en la base de datos

Los ingresos permanentes deberían ser ~5,732 UF/mes pero aparecen multiplicados
"""

import os
import sys
from sqlalchemy import create_engine, text
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
                        return True
    return False


def conectar_produccion():
    """Conecta a la base de datos de producción"""
    cargar_env_produccion()

    if len(sys.argv) > 1:
        database_url = sys.argv[1]
    else:
        database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("❌ No se encontró DATABASE_URL")
        return None

    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.execute(text('SELECT 1'))
        print("✓ Conectado a base de datos de producción")
        return session
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return None


def diagnosticar_duplicacion(session):
    """Diagnostica duplicación de ingresos"""

    print("\n" + "=" * 80)
    print("DIAGNÓSTICO DE DUPLICACIÓN DE INGRESOS")
    print("=" * 80)
    print()

    # 1. Registros duplicados en ingresos_mensuales (mismo servicio + año + mes)
    print("1. REGISTROS DUPLICADOS EN INGRESOS_MENSUALES")
    print("-" * 80)

    result = session.execute(text("""
        SELECT
            im.servicio_id,
            sc.nombre as servicio_nombre,
            c.nombre as cliente_nombre,
            im.año,
            im.mes,
            COUNT(*) as num_registros,
            STRING_AGG(im.id::text, ', ') as ids,
            STRING_AGG(im.ingreso_uf::text, ', ') as valores
        FROM ingresos_mensuales im
        JOIN servicios_cliente sc ON im.servicio_id = sc.id
        JOIN clientes c ON sc.cliente_id = c.id
        GROUP BY im.servicio_id, sc.nombre, c.nombre, im.año, im.mes
        HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC, c.nombre, im.año, im.mes
    """))

    duplicados = list(result)

    if duplicados:
        print(f"\n❌ ENCONTRADOS {len(duplicados)} CASOS DE DUPLICACIÓN:\n")

        total_registros_duplicados = 0
        for row in duplicados[:20]:  # Mostrar primeros 20
            servicio_id, servicio_nombre, cliente_nombre, año, mes, num_registros, ids, valores = row
            total_registros_duplicados += (num_registros - 1)

            print(f"Cliente: {cliente_nombre}")
            print(f"Servicio: {servicio_nombre} (ID: {servicio_id})")
            print(f"Período: {año}-{mes:02d}")
            print(f"Registros duplicados: {num_registros}")
            print(f"IDs: {ids}")
            print(f"Valores: {valores} UF")
            print()

        if len(duplicados) > 20:
            print(f"... y {len(duplicados) - 20} casos más")
            print()

        print(f"TOTAL DE REGISTROS DUPLICADOS A ELIMINAR: {total_registros_duplicados}")
    else:
        print("\n✓ No hay registros duplicados exactos")

    # 2. Ingresos mensuales por tipo de cliente (comparar con esperado)
    print("\n")
    print("2. INGRESOS MENSUALES POR TIPO DE CLIENTE (2025)")
    print("-" * 80)
    print(f"{'Mes':12s} {'Permanente':12s} {'Spot':12s} {'Total':12s}")
    print("-" * 80)

    result = session.execute(text("""
        SELECT
            im.mes,
            SUM(CASE WHEN c.tipo = 'permanente' THEN im.ingreso_uf ELSE 0 END) as ing_permanente,
            SUM(CASE WHEN c.tipo = 'spot' THEN im.ingreso_uf ELSE 0 END) as ing_spot,
            SUM(im.ingreso_uf) as total
        FROM ingresos_mensuales im
        JOIN servicios_cliente sc ON im.servicio_id = sc.id
        JOIN clientes c ON sc.cliente_id = c.id
        WHERE im.año = 2025 AND c.activo = true AND sc.activo = true
        GROUP BY im.mes
        ORDER BY im.mes
    """))

    meses_nombres = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    total_perm = 0
    total_spot = 0

    for mes, ing_perm, ing_spot, total in result:
        print(f"{meses_nombres[mes]:12s} {ing_perm:12.2f} {ing_spot:12.2f} {total:12.2f}")
        total_perm += ing_perm
        total_spot += ing_spot

    print("-" * 80)
    print(f"{'TOTAL':12s} {total_perm:12.2f} {total_spot:12.2f} {total_perm + total_spot:12.2f}")
    print()

    # Comparar con esperado
    print("COMPARACIÓN CON VALORES ESPERADOS:")
    print("-" * 80)

    # Permanentes: 5,732 UF/mes (ene-ago) + 5,892 UF (sep)
    esperado_perm_ene_ago = 5732 * 8
    esperado_perm_sep = 5892
    esperado_perm_total = esperado_perm_ene_ago + esperado_perm_sep

    # Spot: según CSV
    esperado_spot = 1344

    print(f"Permanentes esperado (ene-ago): {esperado_perm_ene_ago:.2f} UF")
    print(f"Permanentes esperado (sep):     {esperado_perm_sep:.2f} UF")
    print(f"Permanentes esperado TOTAL:     {esperado_perm_total:.2f} UF")
    print(f"Permanentes en BD:              {total_perm:.2f} UF")
    print(f"DIFERENCIA:                     {total_perm - esperado_perm_total:.2f} UF")
    print(f"MULTIPLICADO POR:               {total_perm / esperado_perm_total:.2f}x")
    print()
    print(f"Spot esperado:                  {esperado_spot:.2f} UF")
    print(f"Spot en BD:                     {total_spot:.2f} UF")
    print(f"DIFERENCIA:                     {total_spot - esperado_spot:.2f} UF")

    if esperado_spot > 0:
        print(f"MULTIPLICADO POR:               {total_spot / esperado_spot:.2f}x")
    print()

    # 3. Análisis por cliente de duplicación
    print("\n")
    print("3. TOP CLIENTES CON POSIBLE SOBRE-REGISTRO")
    print("-" * 80)

    result = session.execute(text("""
        SELECT
            c.nombre,
            c.tipo,
            COUNT(DISTINCT sc.id) as num_servicios,
            COUNT(im.id) as num_registros_ingresos,
            COUNT(DISTINCT CONCAT(im.año, '-', im.mes)) as meses_distintos,
            SUM(im.ingreso_uf) as total_ingresos
        FROM clientes c
        JOIN servicios_cliente sc ON c.id = sc.cliente_id AND sc.activo = true
        JOIN ingresos_mensuales im ON sc.id = im.servicio_id
        WHERE c.activo = true
        GROUP BY c.id, c.nombre, c.tipo
        ORDER BY SUM(im.ingreso_uf) DESC
        LIMIT 15
    """))

    print(f"{'Cliente':30s} {'Tipo':10s} {'Serv':5s} {'Regs':6s} {'Meses':6s} {'Total UF':10s} {'Reg/Mes':8s}")
    print("-" * 80)

    for nombre, tipo, num_serv, num_regs, meses, total in result:
        ratio = num_regs / meses if meses > 0 else 0
        marca = "⚠️" if ratio > num_serv * 1.1 else "  "
        print(f"{marca} {nombre[:28]:30s} {tipo:10s} {num_serv:5d} {num_regs:6d} {meses:6d} {total:10.2f} {ratio:8.2f}")

    print()
    print("Nota: 'Reg/Mes' debería ser ≈ número de servicios")
    print("      Si es mucho mayor, hay duplicación")

    print("\n")


def main():
    print("\n╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  DIAGNÓSTICO DE DUPLICACIÓN DE INGRESOS".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    session = conectar_produccion()

    if not session:
        sys.exit(1)

    diagnosticar_duplicacion(session)
    session.close()


if __name__ == '__main__':
    main()
