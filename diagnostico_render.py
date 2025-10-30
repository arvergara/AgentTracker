"""
Script de diagnóstico para identificar problemas en Render

Este script verifica:
1. Conexión a la base de datos
2. Estructura de tablas
3. Clientes existentes
4. Personas existentes
5. Registros de horas actuales
"""

import os
from sqlalchemy import create_engine, text, inspect

# Obtener DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL no está configurada")
    print("Ejecuta: export DATABASE_URL='postgresql://...'")
    exit(1)

# Fix para Render (postgres:// -> postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("="*70)
print("DIAGNÓSTICO DE BASE DE DATOS EN RENDER")
print("="*70)
print(f"\nConectando a: {DATABASE_URL[:50]}...\n")

try:
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("✓ Conexión exitosa\n")

        # 1. Verificar estructura de tablas
        print("="*70)
        print("1. ESTRUCTURA DE TABLAS")
        print("="*70)

        inspector = inspect(engine)

        # Tabla clientes
        if inspector.has_table('clientes'):
            print("\n✓ Tabla 'clientes' existe")
            columns = inspector.get_columns('clientes')
            print("  Columnas:")
            for col in columns:
                print(f"    - {col['name']} ({col['type']})")
        else:
            print("\n❌ Tabla 'clientes' NO existe")

        # Tabla personas
        if inspector.has_table('personas'):
            print("\n✓ Tabla 'personas' existe")
            columns = inspector.get_columns('personas')
            print("  Columnas:")
            for col in columns:
                print(f"    - {col['name']} ({col['type']})")
        else:
            print("\n❌ Tabla 'personas' NO existe")

        # Tabla registros_horas
        if inspector.has_table('registros_horas'):
            print("\n✓ Tabla 'registros_horas' existe")
            columns = inspector.get_columns('registros_horas')
            print("  Columnas:")
            for col in columns:
                print(f"    - {col['name']} ({col['type']})")
        else:
            print("\n❌ Tabla 'registros_horas' NO existe")

        # Tabla areas
        if inspector.has_table('areas'):
            print("\n✓ Tabla 'areas' existe")
        else:
            print("\n❌ Tabla 'areas' NO existe")

        # Tabla servicios
        if inspector.has_table('servicios'):
            print("\n✓ Tabla 'servicios' existe")
        else:
            print("\n❌ Tabla 'servicios' NO existe")

        # Tabla tareas
        if inspector.has_table('tareas'):
            print("\n✓ Tabla 'tareas' existe")
        else:
            print("\n❌ Tabla 'tareas' NO existe")

        # 2. Clientes existentes
        print("\n" + "="*70)
        print("2. CLIENTES EXISTENTES")
        print("="*70)

        result = conn.execute(text("SELECT COUNT(*) FROM clientes"))
        count = result.fetchone()[0]
        print(f"\nTotal clientes: {count}")

        result = conn.execute(text("SELECT nombre FROM clientes ORDER BY nombre LIMIT 20"))
        print("\nPrimeros 20 clientes:")
        for row in result:
            print(f"  - {row[0]}")

        # 3. Personas existentes
        print("\n" + "="*70)
        print("3. PERSONAS EXISTENTES")
        print("="*70)

        result = conn.execute(text("SELECT COUNT(*) FROM personas WHERE activo = true"))
        count = result.fetchone()[0]
        print(f"\nTotal personas activas: {count}")

        result = conn.execute(text("SELECT nombre FROM personas WHERE activo = true ORDER BY nombre"))
        print("\nPersonas activas:")
        for row in result:
            print(f"  - {row[0]}")

        # 4. Registros de horas actuales (2025)
        print("\n" + "="*70)
        print("4. REGISTROS DE HORAS (2025)")
        print("="*70)

        result = conn.execute(text("""
            SELECT COUNT(*), SUM(horas)
            FROM registros_horas
            WHERE fecha >= '2025-01-01' AND fecha < '2025-10-01'
        """))
        count, total_horas = result.fetchone()

        print(f"\nTotal registros (2025): {count:,}")
        print(f"Total horas (2025): {total_horas:,.2f}" if total_horas else "Total horas (2025): 0")

        # 5. Verificar clientes específicos del Excel
        print("\n" + "="*70)
        print("5. VERIFICACIÓN DE CLIENTES DEL EXCEL")
        print("="*70)

        clientes_excel = ['CLÍNICAS', 'EBM', 'FALABELLA', 'Falabella', 'EMBAJADA ITALIA', 'Embajada de Italia']

        for cliente in clientes_excel:
            result = conn.execute(text("SELECT id, nombre FROM clientes WHERE UPPER(nombre) = UPPER(:nombre)"),
                                {"nombre": cliente})
            row = result.fetchone()
            if row:
                print(f"  ✓ '{cliente}' -> existe como '{row[1]}' (id: {row[0]})")
            else:
                print(f"  ❌ '{cliente}' -> NO existe")

        # 6. Verificar áreas
        print("\n" + "="*70)
        print("6. ÁREAS EXISTENTES")
        print("="*70)

        result = conn.execute(text("SELECT nombre FROM areas ORDER BY nombre"))
        print("\nÁreas en la base de datos:")
        for row in result:
            print(f"  - {row[0]}")

        print("\n" + "="*70)
        print("✓ DIAGNÓSTICO COMPLETADO")
        print("="*70)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
