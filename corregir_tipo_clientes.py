#!/usr/bin/env python3
"""
Corregir tipo de clientes (permanente vs spot)

Basado en análisis de ingresos regulares vs puntuales
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
        return session, engine
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return None, None


def analizar_clientes(session):
    """Analiza patrones de ingresos para determinar tipo correcto"""

    print("\n" + "=" * 80)
    print("ANÁLISIS DE PATRONES DE INGRESOS")
    print("=" * 80)
    print()

    # Obtener todos los clientes con sus patrones de ingreso
    result = session.execute(text("""
        SELECT
            c.id,
            c.nombre,
            c.tipo as tipo_actual,
            COUNT(DISTINCT CONCAT(im.año, '-', im.mes)) as meses_con_ingresos,
            SUM(im.ingreso_uf) as total_ingresos,
            AVG(im.ingreso_uf) as promedio_ingreso_mes,
            STDDEV(im.ingreso_uf) as desviacion_ingresos,
            MIN(CONCAT(im.año, '-', LPAD(im.mes::text, 2, '0'))) as primer_ingreso,
            MAX(CONCAT(im.año, '-', LPAD(im.mes::text, 2, '0'))) as ultimo_ingreso
        FROM clientes c
        JOIN servicios_cliente sc ON c.id = sc.cliente_id
        JOIN ingresos_mensuales im ON sc.id = im.servicio_id
        WHERE c.activo = true AND sc.activo = true
        GROUP BY c.id, c.nombre, c.tipo
        ORDER BY SUM(im.ingreso_uf) DESC
    """))

    clientes_a_corregir = []

    print("CLIENTES ANALIZADOS:")
    print("-" * 80)
    print(f"{'Cliente':35s} {'Tipo Actual':12s} {'Meses':6s} {'Total UF':10s} {'Prom/mes':10s} {'Sugerencia':15s}")
    print("-" * 80)

    for row in result:
        cliente_id, nombre, tipo_actual, meses, total, promedio, desviacion, primer, ultimo = row

        # Criterios para determinar tipo:
        # PERMANENTE: >= 6 meses con ingresos, desviación baja
        # SPOT: < 6 meses con ingresos O ingresos muy irregulares

        if meses >= 6 and (desviacion is None or desviacion < promedio * 0.5):
            tipo_sugerido = 'permanente'
        elif meses < 6:
            tipo_sugerido = 'spot'
        else:
            # Caso ambiguo, mantener actual
            tipo_sugerido = tipo_actual

        marca = "❌" if tipo_actual != tipo_sugerido else "✓"
        print(f"{nombre[:34]:35s} {tipo_actual:12s} {meses:6d} {total:10.2f} {promedio:10.2f} {tipo_sugerido:15s} {marca}")

        if tipo_actual != tipo_sugerido:
            clientes_a_corregir.append({
                'id': cliente_id,
                'nombre': nombre,
                'tipo_actual': tipo_actual,
                'tipo_sugerido': tipo_sugerido,
                'meses': meses,
                'total': total,
                'promedio': promedio
            })

    print()

    return clientes_a_corregir


def corregir_clientes(session, engine, clientes_a_corregir, ejecutar=False):
    """Corrige el tipo de clientes"""

    if not clientes_a_corregir:
        print("✓ No hay clientes que corregir")
        return

    print("\n" + "=" * 80)
    print("CLIENTES A CORREGIR")
    print("=" * 80)
    print()

    for cliente in clientes_a_corregir:
        print(f"• {cliente['nombre']}")
        print(f"  Actual: {cliente['tipo_actual']} → Nuevo: {cliente['tipo_sugerido']}")
        print(f"  Meses con ingresos: {cliente['meses']}")
        print(f"  Total ingresos: {cliente['total']:.2f} UF")
        print()

    if not ejecutar:
        print("=" * 80)
        print("⚠️  MODO SIMULACIÓN - No se realizaron cambios")
        print("=" * 80)
        print()
        print("Para aplicar estos cambios, ejecuta:")
        print("  python corregir_tipo_clientes.py --ejecutar")
        print()
        return

    # Confirmar
    print("=" * 80)
    print("⚠️  ADVERTENCIA: Vas a modificar el tipo de clientes en PRODUCCIÓN")
    print("=" * 80)
    print()
    respuesta = input("¿Continuar? (escribe 'SI' para confirmar): ")

    if respuesta.strip().upper() != 'SI':
        print("\nOperación cancelada")
        return

    # Ejecutar correcciones
    print("\nAplicando cambios...")
    print("-" * 80)

    corregidos = 0
    with engine.connect() as conn:
        for cliente in clientes_a_corregir:
            try:
                conn.execute(text("""
                    UPDATE clientes
                    SET tipo = :tipo_nuevo
                    WHERE id = :cliente_id
                """), {
                    'tipo_nuevo': cliente['tipo_sugerido'],
                    'cliente_id': cliente['id']
                })
                conn.commit()
                print(f"✓ {cliente['nombre']:40s} {cliente['tipo_actual']} → {cliente['tipo_sugerido']}")
                corregidos += 1
            except Exception as e:
                print(f"❌ Error al corregir {cliente['nombre']}: {e}")
                conn.rollback()

    print()
    print("=" * 80)
    print(f"✓ CORRECCIONES COMPLETADAS: {corregidos} clientes actualizados")
    print("=" * 80)
    print()


def main():
    ejecutar = '--ejecutar' in sys.argv

    print("\n╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  CORRECCIÓN DE TIPO DE CLIENTES (PERMANENTE/SPOT)".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    session, engine = conectar_produccion()

    if not session:
        sys.exit(1)

    # Analizar
    clientes_a_corregir = analizar_clientes(session)

    # Corregir
    if clientes_a_corregir:
        corregir_clientes(session, engine, clientes_a_corregir, ejecutar)
    else:
        print("\n✓ Todos los clientes tienen el tipo correcto")

    session.close()


if __name__ == '__main__':
    main()
