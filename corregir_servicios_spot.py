#!/usr/bin/env python3
"""
Corregir servicios marcados incorrectamente como permanentes cuando deberían ser SPOT
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# IDs de servicios a corregir (SOLO los que están en CSV SPOT)
# Total esperado con datos actuales: 1,133.8 UF (falta OXZO Diagnóstico 210 UF sin registrar)
SERVICIOS_A_CORREGIR = [
    30,  # Capstone - Diseño por 1 vez (70 UF jul)
    31,  # Capstone - Embajadores por 1 vez (65 UF jun)
    32,  # Capstone - Un taller de vocería (200 UF ago)
    51,  # Frutas de Chile - Un Taller de vocería (60 UF jul) [en CSV es "Concha y Toro"]
    52,  # EMBAJADA ITALIA - Asesoría x 4 meses (88.8 UF abr-jul)
    53,  # FALABELLA - Taller de vocería una vez (200 UF mar)
    33,  # FRUTAS DE CHILE - Taller de vocería una vez (200 UF may)
    34,  # OXZO - Diagnóstico una vez (0 UF - debería ser 210 UF feb, falta registrar)
]

# Ya marcado correctamente como SPOT:
# - ID 55: Comité de Paltas - Sept-oct-nov (250 UF) ✓

# Servicios que NO deben marcarse como SPOT (están en permanentes o son incorrectos):
# - ID 26: Capstone - Proyecto HSE (2,000 UF) - NO en CSV SPOT
# - ID 6: EBM - Talleres de vocería (130 UF) - NO en CSV SPOT
# - ID 59: OXZO - Comunicaciones externas (200 UF) - Servicio permanente desde sept
# - ID 50: Comité de Paltas - Posible mapeo incorrecto de "Capital Advisors"
# - ID 51: Frutas de Chile - "Un Taller" (60 UF) - En realidad es "Concha y Toro"

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
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("❌ No se encontró DATABASE_URL")
        return None, None

    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        session.execute(text('SELECT 1'))
        print("✓ Conectado a base de datos de producción")
        return session, engine
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return None, None


def verificar_servicios(session, ids):
    """Verifica los servicios antes de corregir"""

    print("\n" + "=" * 80)
    print("SERVICIOS A CORREGIR")
    print("=" * 80)
    print()

    result = session.execute(text("""
        SELECT
            sc.id,
            c.nombre as cliente,
            sc.nombre as servicio,
            sc.es_spot,
            sc.activo,
            COALESCE(SUM(im.ingreso_uf), 0) as total_ingresos
        FROM servicios_cliente sc
        JOIN clientes c ON sc.cliente_id = c.id
        LEFT JOIN ingresos_mensuales im ON sc.id = im.servicio_id AND im.año = 2025
        WHERE sc.id = ANY(:ids)
        GROUP BY sc.id, c.nombre, sc.nombre, sc.es_spot, sc.activo
        ORDER BY c.nombre, sc.nombre
    """), {'ids': ids})

    servicios = list(result)

    if not servicios:
        print("⚠️  No se encontraron servicios con los IDs proporcionados")
        return []

    print(f"{'ID':5s} {'Cliente':25s} {'Servicio':40s} {'es_spot':9s} {'Total UF':10s}")
    print("-" * 95)

    total_ingresos = 0
    for sc_id, cliente, servicio, es_spot, activo, total_ing in servicios:
        spot_str = "TRUE" if es_spot else "FALSE"
        print(f"{sc_id:5d} {cliente[:24]:25s} {servicio[:39]:40s} {spot_str:9s} {total_ing:10.2f}")
        total_ingresos += total_ing

    print("-" * 95)
    print(f"{'TOTAL A MOVER A SPOT':54s} {total_ingresos:10.2f} UF")
    print()

    return servicios


def corregir_servicios(engine, ids, ejecutar=False):
    """Corrige los servicios marcándolos como es_spot=True"""

    if not ejecutar:
        print("=" * 80)
        print("⚠️  MODO SIMULACIÓN - No se realizarán cambios")
        print("=" * 80)
        print()
        print("Para aplicar estos cambios, ejecuta:")
        print("  python corregir_servicios_spot.py --ejecutar")
        print()
        return

    # Confirmar
    print("=" * 80)
    print("⚠️  ADVERTENCIA: Vas a modificar servicios en PRODUCCIÓN")
    print("=" * 80)
    print()
    print("Esto marcará estos servicios como SPOT (es_spot=True)")
    print("y sus ingresos aparecerán en la sección de ingresos spot.")
    print()
    respuesta = input("¿Continuar? (escribe 'SI' para confirmar): ")

    if respuesta.strip().upper() != 'SI':
        print("\nOperación cancelada")
        return

    # Ejecutar corrección
    print("\nAplicando cambios...")
    print("-" * 80)

    corregidos = 0
    with engine.connect() as conn:
        for servicio_id in ids:
            try:
                conn.execute(text("""
                    UPDATE servicios_cliente
                    SET es_spot = true
                    WHERE id = :servicio_id
                """), {'servicio_id': servicio_id})
                conn.commit()
                print(f"✓ Servicio ID {servicio_id} → es_spot=True")
                corregidos += 1
            except Exception as e:
                print(f"❌ Error al corregir servicio ID {servicio_id}: {e}")
                conn.rollback()

    print()
    print("=" * 80)
    print(f"✓ CORRECCIONES COMPLETADAS: {corregidos} servicios actualizados")
    print("=" * 80)
    print()

    # Verificar nuevo estado
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                COUNT(DISTINCT sc.id) as num_servicios,
                COALESCE(SUM(im.ingreso_uf), 0) as total_ingresos
            FROM servicios_cliente sc
            LEFT JOIN ingresos_mensuales im ON sc.id = im.servicio_id AND im.año = 2025
            WHERE sc.es_spot = true AND sc.activo = true
        """))

        row = result.fetchone()
        print(f"Total servicios SPOT después de corrección: {row[0]}")
        print(f"Total ingresos SPOT 2025: {row[1]:.2f} UF")

    print()


def main():
    ejecutar = '--ejecutar' in sys.argv

    print("\n╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  CORRECCIÓN DE SERVICIOS SPOT".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    session, engine = conectar_produccion()

    if not session:
        sys.exit(1)

    # Verificar servicios
    servicios = verificar_servicios(session, SERVICIOS_A_CORREGIR)

    if servicios:
        # Corregir
        corregir_servicios(engine, SERVICIOS_A_CORREGIR, ejecutar)

    session.close()


if __name__ == '__main__':
    main()
