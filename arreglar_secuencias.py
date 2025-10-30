"""
Script para arreglar las secuencias de PostgreSQL

Este script sincroniza las secuencias auto-incrementales con los IDs máximos actuales.
Ejecutar ANTES de importar_horas_produccion.py si hay errores de "duplicate key"

Uso:
    export DATABASE_URL="postgresql://..."
    python3 arreglar_secuencias.py
"""

import os
from sqlalchemy import create_engine, text

# Obtener DATABASE_URL del ambiente
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL no está configurada")
    print("Ejecuta: export DATABASE_URL='postgresql://...'")
    exit(1)

# Fix para Render (postgres:// -> postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("="*70)
print("ARREGLANDO SECUENCIAS DE POSTGRESQL")
print("="*70)
print(f"\nConectando a: {DATABASE_URL[:50]}...\n")

# Tablas con secuencias auto-incrementales
tablas_con_secuencia = [
    ('personas', 'personas_id_seq'),
    ('clientes', 'clientes_id_seq'),
    ('areas', 'areas_id_seq'),
    ('servicios', 'servicios_id_seq'),
    ('tareas', 'tareas_id_seq'),
    ('registros_horas', 'registros_horas_id_seq'),
]

try:
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("✓ Conexión exitosa\n")

        for tabla, secuencia in tablas_con_secuencia:
            try:
                # Obtener el MAX ID actual
                result = conn.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {tabla}"))
                max_id = result.fetchone()[0]

                # Sincronizar secuencia
                conn.execute(text(f"SELECT setval('{secuencia}', :max_id, true)"), {"max_id": max_id})

                # Verificar
                result = conn.execute(text(f"SELECT last_value FROM {secuencia}"))
                last_value = result.fetchone()[0]

                print(f"  ✓ {tabla:20s} -> MAX ID: {max_id:5d}, Secuencia: {last_value:5d}")

            except Exception as e:
                print(f"  ❌ {tabla:20s} -> Error: {e}")

        conn.commit()

        print("\n" + "="*70)
        print("✓ SECUENCIAS ARREGLADAS")
        print("="*70)
        print("\nAhora puedes ejecutar: python3 importar_horas_produccion.py")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
