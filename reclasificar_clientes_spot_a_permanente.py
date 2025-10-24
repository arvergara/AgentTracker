#!/usr/bin/env python3
"""
Reclasificar clientes SPOT que deberían ser PERMANENTE

Basado en análisis: Los clientes con ingresos regulares mensuales por 22+ meses
deben ser permanentes, no spot.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Clientes a reclasificar de SPOT → PERMANENTE
CLIENTES_A_RECLASIFICAR = [
    'Capstone Copper',
    'FALABELLA',
    'Frutas de Chile',
]

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


def verificar_clientes(session):
    """Verifica los clientes a reclasificar"""

    print("\n" + "=" * 80)
    print("VERIFICACIÓN DE CLIENTES A RECLASIFICAR")
    print("=" * 80)
    print()

    clientes_info = []

    for nombre_cliente in CLIENTES_A_RECLASIFICAR:
        result = session.execute(text("""
            SELECT
                c.id,
                c.nombre,
                c.tipo,
                COUNT(DISTINCT CONCAT(im.año, '-', im.mes)) as meses_con_ingresos,
                SUM(im.ingreso_uf) as total_ingresos,
                COUNT(DISTINCT sc.id) as num_servicios
            FROM clientes c
            LEFT JOIN servicios_cliente sc ON c.id = sc.cliente_id AND sc.activo = true
            LEFT JOIN ingresos_mensuales im ON sc.id = im.servicio_id
            WHERE c.nombre = :nombre_cliente AND c.activo = true
            GROUP BY c.id, c.nombre, c.tipo
        """), {'nombre_cliente': nombre_cliente})

        row = result.fetchone()

        if row:
            cliente_info = {
                'id': row[0],
                'nombre': row[1],
                'tipo_actual': row[2],
                'meses': row[3],
                'total': row[4] or 0,
                'servicios': row[5] or 0
            }
            clientes_info.append(cliente_info)

            marca = "❌" if cliente_info['tipo_actual'] == 'spot' else "✓"
            print(f"{marca} {cliente_info['nombre']:30s}")
            print(f"   Tipo actual: {cliente_info['tipo_actual']}")
            print(f"   Meses con ingresos: {cliente_info['meses']}")
            print(f"   Total ingresos: {cliente_info['total']:.2f} UF")
            print(f"   Servicios activos: {cliente_info['servicios']}")
            print()
        else:
            print(f"⚠️  Cliente no encontrado: {nombre_cliente}")
            print()

    return clientes_info


def reclasificar_clientes(engine, clientes_info, ejecutar=False):
    """Reclasifica los clientes de SPOT a PERMANENTE"""

    clientes_a_cambiar = [c for c in clientes_info if c['tipo_actual'] == 'spot']

    if not clientes_a_cambiar:
        print("✓ Todos los clientes ya tienen el tipo correcto (permanente)")
        return

    print("\n" + "=" * 80)
    print("CLIENTES A RECLASIFICAR: SPOT → PERMANENTE")
    print("=" * 80)
    print()

    total_ingresos_a_mover = sum(c['total'] for c in clientes_a_cambiar)

    for cliente in clientes_a_cambiar:
        print(f"• {cliente['nombre']}")
        print(f"  Cambio: spot → permanente")
        print(f"  Ingresos: {cliente['total']:.2f} UF")
        print()

    print(f"TOTAL INGRESOS A MOVER DE SPOT A PERMANENTE: {total_ingresos_a_mover:.2f} UF")
    print()

    if not ejecutar:
        print("=" * 80)
        print("⚠️  MODO SIMULACIÓN - No se realizaron cambios")
        print("=" * 80)
        print()
        print("Para aplicar estos cambios, ejecuta:")
        print("  python reclasificar_clientes_spot_a_permanente.py --ejecutar")
        print()
        return

    # Confirmar
    print("=" * 80)
    print("⚠️  ADVERTENCIA: Vas a reclasificar clientes en PRODUCCIÓN")
    print("=" * 80)
    print()
    print("Esto afectará:")
    print("- Los totales de ingresos permanentes vs spot en el dashboard")
    print("- Los análisis de capacidad y rentabilidad")
    print("- Los reportes de productividad")
    print()
    respuesta = input("¿Continuar? (escribe 'SI' para confirmar): ")

    if respuesta.strip().upper() != 'SI':
        print("\nOperación cancelada")
        return

    # Ejecutar reclasificación
    print("\nAplicando cambios...")
    print("-" * 80)

    reclasificados = 0
    with engine.connect() as conn:
        for cliente in clientes_a_cambiar:
            try:
                conn.execute(text("""
                    UPDATE clientes
                    SET tipo = 'permanente'
                    WHERE id = :cliente_id
                """), {'cliente_id': cliente['id']})
                conn.commit()
                print(f"✓ {cliente['nombre']:40s} spot → permanente")
                reclasificados += 1
            except Exception as e:
                print(f"❌ Error al reclasificar {cliente['nombre']}: {e}")
                conn.rollback()

    print()
    print("=" * 80)
    print(f"✓ RECLASIFICACIÓN COMPLETADA: {reclasificados} clientes actualizados")
    print("=" * 80)
    print()

    # Verificar nuevo estado
    print("VERIFICANDO NUEVO ESTADO...")
    print("-" * 80)

    with engine.connect() as conn:
        # Ingresos SPOT después de la corrección
        result = conn.execute(text("""
            SELECT
                COUNT(DISTINCT c.id) as num_clientes,
                SUM(im.ingreso_uf) as total_ingresos
            FROM clientes c
            JOIN servicios_cliente sc ON c.id = sc.cliente_id
            JOIN ingresos_mensuales im ON sc.id = im.servicio_id
            WHERE c.tipo = 'spot' AND c.activo = true AND sc.activo = true
        """))

        row = result.fetchone()
        print(f"\nIngresos SPOT después de corrección:")
        print(f"  Clientes: {row[0]}")
        print(f"  Total: {row[1] or 0:.2f} UF")

        # Ingresos PERMANENTES
        result = conn.execute(text("""
            SELECT
                COUNT(DISTINCT c.id) as num_clientes,
                SUM(im.ingreso_uf) as total_ingresos
            FROM clientes c
            JOIN servicios_cliente sc ON c.id = sc.cliente_id
            JOIN ingresos_mensuales im ON sc.id = im.servicio_id
            WHERE c.tipo = 'permanente' AND c.activo = true AND sc.activo = true
        """))

        row = result.fetchone()
        print(f"\nIngresos PERMANENTES después de corrección:")
        print(f"  Clientes: {row[0]}")
        print(f"  Total: {row[1] or 0:.2f} UF")

    print()


def main():
    ejecutar = '--ejecutar' in sys.argv

    print("\n╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  RECLASIFICACIÓN: SPOT → PERMANENTE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    session, engine = conectar_produccion()

    if not session:
        sys.exit(1)

    # Verificar clientes
    clientes_info = verificar_clientes(session)

    # Reclasificar
    if clientes_info:
        reclasificar_clientes(engine, clientes_info, ejecutar)

    session.close()


if __name__ == '__main__':
    main()
