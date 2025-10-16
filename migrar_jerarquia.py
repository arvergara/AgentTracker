"""
Script de migración para agregar campos de jerarquía a la base de datos

Agrega:
- es_admin (Boolean)
- reporte_a_id (Integer, ForeignKey)
"""

import sqlite3
import os

def migrar_base_datos():
    """Agrega columnas de jerarquía a la tabla personas"""

    db_path = 'comsulting_simplified.db'

    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        print("Ejecuta la aplicación primero para crear la base de datos.")
        return

    print("="*80)
    print("MIGRACIÓN: Agregar campos de jerarquía organizacional")
    print("="*80)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(personas)")
        columnas = [col[1] for col in cursor.fetchall()]

        print(f"\nColumnas actuales en tabla personas:")
        for col in columnas:
            print(f"  • {col}")

        # Agregar es_admin si no existe
        if 'es_admin' not in columnas:
            print("\n➕ Agregando columna 'es_admin'...")
            cursor.execute("ALTER TABLE personas ADD COLUMN es_admin BOOLEAN DEFAULT 0")
            print("✓ Columna 'es_admin' agregada")
        else:
            print("\n✓ Columna 'es_admin' ya existe")

        # Agregar reporte_a_id si no existe
        if 'reporte_a_id' not in columnas:
            print("➕ Agregando columna 'reporte_a_id'...")
            cursor.execute("ALTER TABLE personas ADD COLUMN reporte_a_id INTEGER")
            print("✓ Columna 'reporte_a_id' agregada")
        else:
            print("✓ Columna 'reporte_a_id' ya existe")

        conn.commit()

        # Verificar resultados
        cursor.execute("PRAGMA table_info(personas)")
        columnas_nuevas = [col[1] for col in cursor.fetchall()]

        print(f"\nColumnas después de la migración:")
        for col in columnas_nuevas:
            print(f"  • {col}")

        # Mostrar conteo de personas
        cursor.execute("SELECT COUNT(*) FROM personas")
        total = cursor.fetchone()[0]

        print(f"\nTotal de personas en la base de datos: {total}")

        print("\n" + "="*80)
        print("✓ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*80)
        print("\nPróximos pasos:")
        print("  1. Ejecutar: python configurar_jerarquia_organigrama.py")
        print("  2. Esto configurará:")
        print("     - Administradores (Blanca, Macarena, Jazmín)")
        print("     - Relaciones de reporte según organigrama")
        print("="*80)

    except sqlite3.Error as e:
        print(f"\n❌ Error en la migración: {e}")
        conn.rollback()

    finally:
        conn.close()

if __name__ == '__main__':
    migrar_base_datos()
