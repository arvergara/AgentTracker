#!/usr/bin/env python3
"""
Buscar servicios SPOT faltantes
"""

import os
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

cargar_env_produccion()
database_url = os.environ.get('DATABASE_URL')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
session = Session()

print("\n1. Buscando 'Capital Advisors' o 'Comité de Paltas'...")
result = session.execute(text("""
    SELECT
        sc.id,
        c.nombre as cliente,
        sc.nombre as servicio,
        sc.es_spot,
        COALESCE(SUM(im.ingreso_uf), 0) as total
    FROM servicios_cliente sc
    JOIN clientes c ON sc.cliente_id = c.id
    LEFT JOIN ingresos_mensuales im ON sc.id = im.servicio_id AND im.año = 2025
    WHERE (UPPER(c.nombre) LIKE '%CAPITAL%' OR UPPER(c.nombre) LIKE '%COMITE%' OR UPPER(c.nombre) LIKE '%PALTA%')
    GROUP BY sc.id, c.nombre, sc.nombre, sc.es_spot
    ORDER BY c.nombre
"""))

for row in result:
    print(f"  ID {row[0]}: {row[1]} - {row[2]} (es_spot={row[3]}) = {row[4]:.2f} UF")

print("\n2. Buscando 'Concha y Toro'...")
result = session.execute(text("""
    SELECT
        sc.id,
        c.nombre as cliente,
        sc.nombre as servicio,
        sc.es_spot,
        COALESCE(SUM(im.ingreso_uf), 0) as total
    FROM servicios_cliente sc
    JOIN clientes c ON sc.cliente_id = c.id
    LEFT JOIN ingresos_mensuales im ON sc.id = im.servicio_id AND im.año = 2025
    WHERE UPPER(c.nombre) LIKE '%CONCHA%'
    GROUP BY sc.id, c.nombre, sc.nombre, sc.es_spot
    ORDER BY c.nombre
"""))

for row in result:
    print(f"  ID {row[0]}: {row[1]} - {row[2]} (es_spot={row[3]}) = {row[4]:.2f} UF")

print("\n3. Buscando servicios de 'Frutas de Chile' con 60 UF...")
result = session.execute(text("""
    SELECT
        sc.id,
        c.nombre as cliente,
        sc.nombre as servicio,
        sc.es_spot,
        COALESCE(SUM(im.ingreso_uf), 0) as total
    FROM servicios_cliente sc
    JOIN clientes c ON sc.cliente_id = c.id
    LEFT JOIN ingresos_mensuales im ON sc.id = im.servicio_id AND im.año = 2025
    WHERE UPPER(c.nombre) LIKE '%FRUTAS%'
    GROUP BY sc.id, c.nombre, sc.nombre, sc.es_spot
    HAVING COALESCE(SUM(im.ingreso_uf), 0) BETWEEN 50 AND 70
    ORDER BY c.nombre
"""))

for row in result:
    print(f"  ID {row[0]}: {row[1]} - {row[2]} (es_spot={row[3]}) = {row[4]:.2f} UF")

print("\n4. Desglose de ingresos OXZO Diagnóstico (ID 34)...")
result = session.execute(text("""
    SELECT
        im.año,
        im.mes,
        im.ingreso_uf
    FROM ingresos_mensuales im
    WHERE im.servicio_id = 34
    ORDER BY im.año, im.mes
"""))

ingresos_oxzo = list(result)
if ingresos_oxzo:
    for año, mes, monto in ingresos_oxzo:
        print(f"  {año}-{mes:02d}: {monto:.2f} UF")
else:
    print("  ⚠️  No hay ingresos registrados para este servicio")

print("\n5. Buscando OXZO con 210 UF...")
result = session.execute(text("""
    SELECT
        sc.id,
        c.nombre as cliente,
        sc.nombre as servicio,
        sc.es_spot,
        im.año,
        im.mes,
        im.ingreso_uf
    FROM servicios_cliente sc
    JOIN clientes c ON sc.cliente_id = c.id
    JOIN ingresos_mensuales im ON sc.id = im.servicio_id
    WHERE UPPER(c.nombre) LIKE '%OXZO%'
        AND im.ingreso_uf BETWEEN 200 AND 220
        AND im.año = 2025
    ORDER BY im.mes
"""))

for row in result:
    print(f"  ID {row[0]}: {row[1]} - {row[2]} ({row[3]}) {row[4]}-{row[5]:02d}: {row[6]:.2f} UF")

session.close()
