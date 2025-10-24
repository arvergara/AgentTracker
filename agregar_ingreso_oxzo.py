#!/usr/bin/env python3
"""
Agregar ingreso faltante de OXZO Diagnóstico (210 UF en febrero 2025)
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def cargar_env_produccion():
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


def main():
    ejecutar = '--ejecutar' in sys.argv

    print("\n╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  AGREGAR INGRESO FALTANTE: OXZO DIAGNÓSTICO".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    session, engine = conectar_produccion()

    if not session:
        sys.exit(1)

    # Verificar servicio OXZO Diagnóstico
    print("Verificando servicio OXZO Diagnóstico (ID 34)...")
    print("-" * 80)

    result = session.execute(text("""
        SELECT
            sc.id,
            c.nombre as cliente,
            sc.nombre as servicio,
            sc.es_spot
        FROM servicios_cliente sc
        JOIN clientes c ON sc.cliente_id = c.id
        WHERE sc.id = 34
    """))

    servicio = result.fetchone()

    if servicio:
        print(f"ID: {servicio[0]}")
        print(f"Cliente: {servicio[1]}")
        print(f"Servicio: {servicio[2]}")
        print(f"es_spot: {servicio[3]}")
    else:
        print("❌ No se encontró el servicio ID 34")
        sys.exit(1)

    # Verificar si ya existe el ingreso
    print("\nVerificando ingresos existentes para este servicio...")
    result = session.execute(text("""
        SELECT año, mes, ingreso_uf
        FROM ingresos_mensuales
        WHERE servicio_id = 34
        ORDER BY año, mes
    """))

    ingresos_existentes = list(result)

    if ingresos_existentes:
        print("\nIngresos existentes:")
        for año, mes, monto in ingresos_existentes:
            print(f"  {año}-{mes:02d}: {monto:.2f} UF")
    else:
        print("  No hay ingresos registrados")

    # Verificar si existe febrero 2025
    existe_feb_2025 = any(año == 2025 and mes == 2 for año, mes, _ in ingresos_existentes)

    if existe_feb_2025:
        print("\n⚠️  Ya existe un ingreso para febrero 2025")
        ingreso_actual = next((monto for año, mes, monto in ingresos_existentes if año == 2025 and mes == 2), 0)
        print(f"   Valor actual: {ingreso_actual:.2f} UF")
        print(f"   Valor esperado: 210.00 UF")

        if abs(ingreso_actual - 210) < 0.01:
            print("\n✓ El ingreso ya está correcto")
            return
    else:
        print("\n⚠️  Falta registrar ingreso de febrero 2025 (210 UF)")

    if not ejecutar:
        print("\n" + "=" * 80)
        print("⚠️  MODO SIMULACIÓN - No se realizarán cambios")
        print("=" * 80)
        print()
        print("Para aplicar estos cambios, ejecuta:")
        print("  python agregar_ingreso_oxzo.py --ejecutar")
        print()
        return

    # Confirmar
    print("\n" + "=" * 80)
    print("⚠️  ADVERTENCIA: Vas a agregar/modificar ingresos en PRODUCCIÓN")
    print("=" * 80)
    print()
    print("Se agregará:")
    print("  Servicio ID: 34 (OXZO - Diagnóstico)")
    print("  Año: 2025")
    print("  Mes: 2 (febrero)")
    print("  Ingreso: 210 UF")
    print()
    respuesta = input("¿Continuar? (escribe 'SI' para confirmar): ")

    if respuesta.strip().upper() != 'SI':
        print("\nOperación cancelada")
        return

    # Ejecutar
    print("\nAplicando cambios...")
    print("-" * 80)

    with engine.connect() as conn:
        try:
            if existe_feb_2025:
                # Actualizar
                conn.execute(text("""
                    UPDATE ingresos_mensuales
                    SET ingreso_uf = 210
                    WHERE servicio_id = 34 AND año = 2025 AND mes = 2
                """))
                print("✓ Ingreso actualizado: 2025-02 → 210 UF")
            else:
                # Insertar
                conn.execute(text("""
                    INSERT INTO ingresos_mensuales (servicio_id, año, mes, ingreso_uf)
                    VALUES (34, 2025, 2, 210)
                """))
                print("✓ Ingreso agregado: 2025-02 → 210 UF")

            conn.commit()

            print()
            print("=" * 80)
            print("✓ OPERACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 80)

            # Verificar total SPOT
            result = conn.execute(text("""
                SELECT
                    COUNT(DISTINCT sc.id) as num_servicios,
                    COALESCE(SUM(im.ingreso_uf), 0) as total_ingresos
                FROM servicios_cliente sc
                LEFT JOIN ingresos_mensuales im ON sc.id = im.servicio_id AND im.año = 2025
                WHERE sc.es_spot = true AND sc.activo = true
            """))

            row = result.fetchone()
            print(f"\nTotal servicios SPOT: {row[0]}")
            print(f"Total ingresos SPOT 2025: {row[1]:.2f} UF")
            print()

        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()

    session.close()


if __name__ == '__main__':
    main()
