#!/usr/bin/env python3
"""
Inspeccionar estructura de la base de datos de producción
"""

import os
import sys
from sqlalchemy import create_engine, inspect, text
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


def inspeccionar_db():
    """Inspecciona la estructura de la base de datos"""

    # Cargar env
    cargar_env_produccion()

    # Obtener DATABASE_URL
    if len(sys.argv) > 1:
        database_url = sys.argv[1]
    else:
        database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("❌ No se encontró DATABASE_URL")
        return

    # Corregir formato
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    print("\n" + "=" * 80)
    print("INSPECCIÓN DE BASE DE DATOS DE PRODUCCIÓN")
    print("=" * 80)
    print()

    try:
        engine = create_engine(database_url)
        inspector = inspect(engine)

        # Obtener todas las tablas
        tables = inspector.get_table_names()

        print(f"✓ Conectado a base de datos")
        print(f"✓ Encontradas {len(tables)} tablas")
        print()

        if not tables:
            print("⚠️  LA BASE DE DATOS ESTÁ VACÍA")
            print()
            print("La base de datos no tiene ninguna tabla.")
            print("Necesitas inicializarla primero ejecutando en Render:")
            print("  python app.py")
            print("  O visita: https://tu-app.onrender.com/inicializar-datos")
            return

        print("TABLAS ENCONTRADAS:")
        print("-" * 80)

        for table_name in sorted(tables):
            # Obtener número de registros
            with engine.connect() as conn:
                result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
                count = result.scalar()

            print(f"  {table_name:30s} {count:6d} registros")

        print()

        # Si hay tablas, verificar específicamente las que necesitamos
        tablas_requeridas = ['cliente', 'servicios_cliente', 'ingresos_mensuales', 'persona']

        print("VERIFICACIÓN DE TABLAS REQUERIDAS:")
        print("-" * 80)

        for tabla in tablas_requeridas:
            if tabla in tables:
                with engine.connect() as conn:
                    result = conn.execute(text(f'SELECT COUNT(*) FROM "{tabla}"'))
                    count = result.scalar()
                print(f"  ✓ {tabla:30s} {count:6d} registros")
            else:
                print(f"  ❌ {tabla:30s} NO EXISTE")

        print()

        # Si existen las tablas de clientes, mostrar tipos
        if 'cliente' in tables:
            print("CLIENTES POR TIPO:")
            print("-" * 80)

            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT tipo, COUNT(*) as total
                    FROM cliente
                    WHERE activo = true
                    GROUP BY tipo
                    ORDER BY tipo
                """))

                for tipo, total in result:
                    print(f"  {tipo or 'Sin tipo':15s}: {total:3d} clientes")

            print()

        # Si existen ingresos, mostrar resumen
        if 'ingresos_mensuales' in tables and 'cliente' in tables and 'servicios_cliente' in tables:
            print("RESUMEN DE INGRESOS:")
            print("-" * 80)

            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT
                        c.tipo,
                        COUNT(DISTINCT c.id) as num_clientes,
                        COALESCE(SUM(im.ingreso_uf), 0) as total_ingresos
                    FROM cliente c
                    LEFT JOIN servicios_cliente sc ON c.id = sc.cliente_id AND sc.activo = true
                    LEFT JOIN ingresos_mensuales im ON sc.id = im.servicio_id
                    WHERE c.activo = true
                    GROUP BY c.tipo
                    ORDER BY c.tipo
                """))

                total_general = 0
                for tipo, num_clientes, total_ingresos in result:
                    print(f"  {tipo or 'Sin tipo':15s}: {num_clientes:3d} clientes, {total_ingresos:10.2f} UF")
                    total_general += total_ingresos

                print(f"\n  {'TOTAL':15s}: {total_general:10.2f} UF")

            print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    inspeccionar_db()
