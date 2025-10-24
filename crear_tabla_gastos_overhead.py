#!/usr/bin/env python3
"""
Script de migración: Crear tabla gastos_overhead para almacenar costos operacionales mensuales

Uso:
    python crear_tabla_gastos_overhead.py          # Simulación (no ejecuta)
    python crear_tabla_gastos_overhead.py --ejecutar  # Ejecuta cambios reales
"""

import os
import sys
from sqlalchemy import create_engine, text, MetaData

# Configuración de base de datos
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Render usa postgres:// pero SQLAlchemy necesita postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
else:
    # Local usa SQLite
    DATABASE_URL = 'sqlite:///comsulting_simplified.db'

print("=" * 80)
print("MIGRACIÓN: Crear tabla gastos_overhead")
print("=" * 80)
print(f"\nBase de datos: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

# SQL para crear tabla
SQL_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS gastos_overhead (
    id SERIAL PRIMARY KEY,
    año INTEGER NOT NULL,
    mes INTEGER NOT NULL CHECK (mes >= 1 AND mes <= 12),
    concepto VARCHAR(200) NOT NULL,
    categoria VARCHAR(100),
    monto_pesos FLOAT NOT NULL DEFAULT 0,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Índices para búsquedas rápidas
    CONSTRAINT unique_año_mes_concepto UNIQUE (año, mes, concepto)
);

CREATE INDEX IF NOT EXISTS idx_gastos_overhead_año_mes ON gastos_overhead(año, mes);
CREATE INDEX IF NOT EXISTS idx_gastos_overhead_categoria ON gastos_overhead(categoria);
"""

# SQL para SQLite (compatible)
SQL_CREATE_TABLE_SQLITE = """
CREATE TABLE IF NOT EXISTS gastos_overhead (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    año INTEGER NOT NULL,
    mes INTEGER NOT NULL CHECK (mes >= 1 AND mes <= 12),
    concepto VARCHAR(200) NOT NULL,
    categoria VARCHAR(100),
    monto_pesos REAL NOT NULL DEFAULT 0,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(año, mes, concepto)
);

CREATE INDEX IF NOT EXISTS idx_gastos_overhead_año_mes ON gastos_overhead(año, mes);
CREATE INDEX IF NOT EXISTS idx_gastos_overhead_categoria ON gastos_overhead(categoria);
"""

def verificar_tabla_existe(engine):
    """Verifica si la tabla ya existe"""
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return 'gastos_overhead' in metadata.tables

def main():
    modo_simulacion = '--ejecutar' not in sys.argv

    if modo_simulacion:
        print("\n⚠️  MODO SIMULACIÓN - No se ejecutarán cambios")
        print("   Para ejecutar: python crear_tabla_gastos_overhead.py --ejecutar\n")
    else:
        print("\n🔧 MODO EJECUCIÓN - Se aplicarán cambios en la base de datos\n")

    # Crear engine
    engine = create_engine(DATABASE_URL)

    # Verificar si tabla ya existe
    tabla_existe = verificar_tabla_existe(engine)

    if tabla_existe:
        print("✅ La tabla 'gastos_overhead' ya existe")
        return

    # Mostrar SQL que se ejecutará
    is_sqlite = 'sqlite' in DATABASE_URL.lower()
    sql_a_ejecutar = SQL_CREATE_TABLE_SQLITE if is_sqlite else SQL_CREATE_TABLE

    print("\n📝 SQL a ejecutar:")
    print("-" * 80)
    print(sql_a_ejecutar)
    print("-" * 80)

    if modo_simulacion:
        print("\n✅ Simulación completada. Ejecuta con --ejecutar para aplicar cambios.")
        return

    # Confirmación manual
    print("\n⚠️  ¿Deseas ejecutar estos cambios en la base de datos?")
    respuesta = input("   Escribe 'SI' para confirmar: ")

    if respuesta.strip().upper() != 'SI':
        print("\n❌ Operación cancelada")
        return

    # Ejecutar migración
    try:
        with engine.begin() as conn:
            # Ejecutar cada statement por separado
            for statement in sql_a_ejecutar.split(';'):
                if statement.strip():
                    conn.execute(text(statement))

        print("\n✅ Migración completada exitosamente")
        print("\n📊 Estructura de tabla 'gastos_overhead':")
        print("   - id: Identificador único")
        print("   - año: Año del gasto (ej: 2025)")
        print("   - mes: Mes del gasto (1-12)")
        print("   - concepto: Descripción del gasto (ej: 'Arriendo oficina')")
        print("   - categoria: Categoría del gasto (ej: 'Oficina', 'Servicios')")
        print("   - monto_pesos: Monto en pesos chilenos")
        print("   - descripcion: Descripción adicional (opcional)")
        print("   - created_at: Fecha de creación del registro")
        print("\n✅ Índices creados para optimizar búsquedas por año/mes")

    except Exception as e:
        print(f"\n❌ Error al ejecutar migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
