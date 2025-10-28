#!/usr/bin/env python3
"""
Script para resetear las secuencias de PostgreSQL cuando están desincronizadas
"""
import os
from sqlalchemy import create_engine, text

# Obtener DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL no configurada")
    print("Ejecuta: export DATABASE_URL='postgresql://...'")
    exit(1)

# Convertir postgres:// a postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("=" * 80)
print("RESETEAR SECUENCIAS DE PostgreSQL")
print("=" * 80)
print(f"Base de datos: {DATABASE_URL.split('@')[-1]}\n")

engine = create_engine(DATABASE_URL)

# Resetear secuencias
with engine.connect() as conn:
    print("Reseteando secuencias...")

    # Clientes
    result = conn.execute(text("SELECT setval('clientes_id_seq', (SELECT MAX(id) FROM clientes))"))
    print(f"✅ clientes_id_seq → {result.scalar()}")

    # Servicios
    result = conn.execute(text("SELECT setval('servicios_cliente_id_seq', (SELECT MAX(id) FROM servicios_cliente))"))
    print(f"✅ servicios_cliente_id_seq → {result.scalar()}")

    # Personas
    result = conn.execute(text("SELECT setval('personas_id_seq', (SELECT MAX(id) FROM personas))"))
    print(f"✅ personas_id_seq → {result.scalar()}")

    # IngresoMensual
    result = conn.execute(text("SELECT setval('ingresos_mensuales_id_seq', (SELECT MAX(id) FROM ingresos_mensuales))"))
    print(f"✅ ingresos_mensuales_id_seq → {result.scalar()}")

    conn.commit()

print("\n✅ Secuencias reseteadas exitosamente")
print("=" * 80)
