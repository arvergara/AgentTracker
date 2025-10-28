#!/usr/bin/env python3
"""
Script unificado para crear tabla e importar datos de overhead en Render

Uso:
    export DATABASE_URL="postgresql://user:pass@host/db"
    python setup_overhead_render.py
"""

import os
import sys
import json
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Verificar DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("=" * 80)
    print("❌ ERROR: Variable DATABASE_URL no configurada")
    print("=" * 80)
    print("\nPara obtener el DATABASE_URL de Render:")
    print("1. Ve a https://dashboard.render.com")
    print("2. Selecciona tu servicio 'AgentTracker'")
    print("3. Ve a 'Environment' en el menú izquierdo")
    print("4. Copia el valor de DATABASE_URL")
    print("\nLuego ejecuta:")
    print('   export DATABASE_URL="postgresql://..."')
    print("   python setup_overhead_render.py")
    sys.exit(1)

# Convertir postgres:// a postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("=" * 80)
print("SETUP DE OVERHEAD EN RENDER")
print("=" * 80)
print(f"\n🔗 Conectando a: {DATABASE_URL.split('@')[-1]}\n")

# Crear engine
engine = create_engine(DATABASE_URL)

# ============= PASO 1: CREAR TABLA =============
print("\n" + "=" * 80)
print("PASO 1: CREAR TABLA gastos_overhead")
print("=" * 80)

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
    CONSTRAINT unique_año_mes_concepto UNIQUE (año, mes, concepto)
);

CREATE INDEX IF NOT EXISTS idx_gastos_overhead_año_mes ON gastos_overhead(año, mes);
CREATE INDEX IF NOT EXISTS idx_gastos_overhead_categoria ON gastos_overhead(categoria);
"""

# Verificar si tabla existe
metadata = MetaData()
metadata.reflect(bind=engine)
tabla_existe = 'gastos_overhead' in metadata.tables

if tabla_existe:
    print("✅ La tabla 'gastos_overhead' ya existe")
else:
    print("📝 Creando tabla 'gastos_overhead'...")
    try:
        with engine.begin() as conn:
            for statement in SQL_CREATE_TABLE.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
        print("✅ Tabla creada exitosamente")
    except Exception as e:
        print(f"❌ Error al crear tabla: {e}")
        sys.exit(1)

# ============= PASO 2: IMPORTAR DATOS =============
print("\n" + "=" * 80)
print("PASO 2: IMPORTAR DATOS DE OVERHEAD")
print("=" * 80)

# Leer JSON
json_path = 'gastos_overhead_2025_real.json'

if not os.path.exists(json_path):
    print(f"\n❌ Error: No se encontró {json_path}")
    sys.exit(1)

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

gastos_por_mes = data['gastos_por_mes']
resumen = data['resumen']

print(f"\n📂 Datos cargados: {len(gastos_por_mes)} registros mensuales")
print(f"💰 Total anual: ${resumen['total_pesos']:,.0f} = {resumen['total_uf']:.2f} UF")

# Verificar si ya existen datos
Session = sessionmaker(bind=engine)
session = Session()

existing_count = session.execute(
    text("SELECT COUNT(*) FROM gastos_overhead WHERE año = 2025")
).scalar()

if existing_count > 0:
    print(f"\n⚠️  Ya existen {existing_count} registros para 2025 en Render")
    respuesta = input("   ¿Deseas eliminarlos y reimportar? (SI/NO): ")

    if respuesta.strip().upper() == 'SI':
        session.execute(text("DELETE FROM gastos_overhead WHERE año = 2025"))
        session.commit()
        print("   ✅ Registros anteriores eliminados")
    else:
        print("   ❌ Importación cancelada")
        session.close()
        sys.exit(0)

# Importar datos
print("\n📥 Importando gastos overhead...")

for gasto_mes in gastos_por_mes:
    sql = text("""
        INSERT INTO gastos_overhead (año, mes, concepto, categoria, monto_pesos, created_at)
        VALUES (:año, :mes, :concepto, :categoria, :monto_pesos, :created_at)
    """)

    session.execute(sql, {
        'año': gasto_mes['año'],
        'mes': gasto_mes['mes'],
        'concepto': gasto_mes['concepto'],
        'categoria': gasto_mes['categoria'],
        'monto_pesos': float(gasto_mes['monto_pesos']),
        'created_at': datetime.now()
    })

    print(f"   {gasto_mes['mes_nombre']:>12}: ${gasto_mes['monto_pesos']:>15,.0f} = {gasto_mes['monto_uf']:>8,.2f} UF")

# Commit
try:
    session.commit()
    print(f"\n✅ Importación completada: {len(gastos_por_mes)} registros")

    # Verificar
    print("\n📊 Verificación en Render:")
    total_result = session.execute(
        text("SELECT SUM(monto_pesos) FROM gastos_overhead WHERE año = 2025")
    )
    suma_bd = total_result.scalar() or 0

    print(f"   Total en BD:      ${suma_bd:>15,.0f}")
    print(f"   Total esperado:   ${resumen['total_pesos']:>15,.0f}")

    diferencia = abs(suma_bd - resumen['total_pesos'])
    if diferencia < 1:
        print(f"   ✅ Verificación exitosa (diferencia: ${diferencia:,.2f})")
    else:
        print(f"   ⚠️  Diferencia:       ${diferencia:>15,.0f}")

except Exception as e:
    session.rollback()
    print(f"\n❌ Error al importar: {e}")
    import traceback
    traceback.print_exc()
    session.close()
    sys.exit(1)

session.close()

# ============= PASO 3: VERIFICAR DEPLOYMENT =============
print("\n" + "=" * 80)
print("PASO 3: VERIFICAR DEPLOYMENT")
print("=" * 80)
print("\nRender debería haber desplegado los cambios automáticamente.")
print("\n📋 Próximos pasos:")
print("1. Ve a https://dashboard.render.com y verifica que el deploy esté completo")
print("2. Accede a https://agenttracker.onrender.com/rentabilidad")
print("3. Verifica que ahora se muestre el overhead distribuido por cliente")
print("\n✅ Setup completado en Render!")
print("=" * 80)
